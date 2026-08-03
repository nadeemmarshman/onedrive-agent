"""
Tests for verify_dedup_invariants.py -- the standing-practice post-action
gate adopted after RAID's v1.0 (omitted work, reconciliation couldn't see
it) and v1.1 (over-quarantined a keeper, dry-run/preflight couldn't see
it) findings. Both defects were only caught by an external check with an
independent notion of the correct end state; this script is that check,
made permanent and reusable rather than ad hoc.

Uses real temp directories and real file content -- the whole point of
this tool is content-hash correctness, which a mocked filesystem would
not meaningfully exercise.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from verify_dedup_invariants import verify


class TestVerifyDedupInvariants(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.live = self.tmp / "live"
        self.quarantine = self.live / "_quarantine"
        self.live.mkdir()
        self.quarantine.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, rel_path: str, content: bytes) -> Path:
        p = self.live / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return p

    def _scan_json(self, groups: list[dict]) -> Path:
        p = self.tmp / "scan.json"
        p.write_text(json.dumps({"groups": groups}), encoding="utf-8")
        return p

    def test_healthy_group_passes(self):
        # Exactly one live copy remains -- the normal, correct post-
        # quarantine state.
        kept = self._write("a.txt", b"hello")
        moved_original = self.live / "b.txt"  # never existed after quarantine
        scan = self._scan_json([{
            "size_bytes": 5,
            "suggested_keeper": str(kept),
            "members": [str(kept), str(moved_original)],
        }])
        result = verify(scan, self.live, self.quarantine)
        self.assertEqual(len(result["orphaned"]), 0)
        self.assertEqual(result["ok"], 1)

    def test_true_orphan_fails_the_gate(self):
        # THE defect this tool exists to catch: every copy is gone from
        # the live tree (moved to quarantine, or deleted), so the group's
        # content does not survive anywhere live.
        (self.quarantine / "a.txt").write_bytes(b"orphaned")
        scan = self._scan_json([{
            "size_bytes": 8,
            "suggested_keeper": str(self.live / "a.txt"),
            "members": [str(self.live / "a.txt"), str(self.quarantine / "a.txt")],
        }])
        result = verify(scan, self.live, self.quarantine)
        self.assertEqual(len(result["orphaned"]), 1)
        self.assertEqual(result["ok"], 0)

    def test_over_retained_is_reported_not_treated_as_failure(self):
        # Two live copies of the same content -- expected while a
        # quarantine folder still holds the duplicate awaiting delete,
        # or (as in the real v1.1 case) right after a restore. Not a
        # gate failure on its own.
        self._write("a.txt", b"dup")
        self._write("b.txt", b"dup")
        scan = self._scan_json([{
            "size_bytes": 3,
            "suggested_keeper": str(self.live / "a.txt"),
            "members": [str(self.live / "a.txt"), str(self.live / "b.txt")],
        }])
        result = verify(scan, self.live, self.quarantine)
        self.assertEqual(len(result["orphaned"]), 0)
        self.assertEqual(len(result["over_retained"]), 1)

    def test_zero_byte_groups_are_excluded(self):
        # Matches quarantine_documents_internal_duplicates_20260803.py's
        # own exclusion of zero-byte false-positive groups.
        scan = self._scan_json([{
            "size_bytes": 0,
            "suggested_keeper": str(self.live / "empty.txt"),
            "members": [str(self.live / "empty.txt"), str(self.live / "empty2.txt")],
        }])
        result = verify(scan, self.live, self.quarantine)
        self.assertEqual(result["groups_checked"], 0)

    def test_quarantine_copy_alone_does_not_satisfy_the_gate(self):
        # A copy existing only in quarantine must not count as "live" --
        # exactly the distinction the exclude parameter exists to enforce.
        (self.quarantine / "only_copy.txt").write_bytes(b"content")
        scan = self._scan_json([{
            "size_bytes": 7,
            "suggested_keeper": str(self.quarantine / "only_copy.txt"),
            "members": [str(self.quarantine / "only_copy.txt")],
        }])
        result = verify(scan, self.live, self.quarantine)
        self.assertEqual(len(result["orphaned"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
