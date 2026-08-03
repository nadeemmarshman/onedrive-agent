"""
Tests for scan_documents_dedup.py's _classify(), pinning the fix for the
classifier gap found by an independent post-action re-scan (Cowork,
2026-08-03): a group with 1 backup copy + 3 live-tree copies was labelled
only "docfolderbackup_vs_live", so its 3-way live-tree redundancy was
never reported or actioned -- 238 of 242 previously-flagged groups were
still duplicated on disk after the phase that was supposed to resolve
them. See COWORK_RECONCILIATION_FINDING_v1.0.md.

The fix makes classification multi-label. These tests exist specifically
so that property cannot silently regress back to single-label behaviour.
"""

import unittest

from scan_documents_dedup import _classify

BACKUP = r"C:\...\DocFolderBackup\Documents\file.ext"
LIVE_A = r"C:\...\00-My Folders\a\file.ext"
LIVE_B = r"C:\...\00-My Folders\b\file.ext"
LIVE_C = r"C:\...\00-My Folders\c\file.ext"
BACKUP_B = r"C:\...\DocFolderBackup\Documents\sub\file.ext"


def group(*paths):
    return [{"path": p} for p in paths]


class TestClassify(unittest.TestCase):
    def test_regression_mixed_group_with_multiple_live_copies(self):
        # THE bug: 1 backup + 3 live. Old classifier returned only
        # "docfolderbackup_vs_live", so the live-tree redundancy (2
        # removable copies beyond the first) was invisible to every
        # downstream report and action queue.
        labels = _classify(group(BACKUP, LIVE_A, LIVE_B, LIVE_C))
        self.assertIn("docfolderbackup_vs_live", labels)
        self.assertIn("internal_duplicate_in_live_tree", labels)

    def test_simple_backup_live_pair_unaffected(self):
        # The one shape the old classifier got right; must not regress.
        labels = _classify(group(BACKUP, LIVE_A))
        self.assertEqual(labels, ["docfolderbackup_vs_live"])

    def test_live_only_internal_duplicate(self):
        labels = _classify(group(LIVE_A, LIVE_B))
        self.assertEqual(labels, ["internal_duplicate_in_live_tree"])

    def test_backup_only_internal_duplicate(self):
        labels = _classify(group(BACKUP, BACKUP_B))
        self.assertEqual(labels, ["internal_duplicate_within_backup"])

    def test_all_three_labels_can_coexist(self):
        # 2 backup + 2 live: spans the boundary AND has internal
        # duplication on both sides simultaneously.
        labels = _classify(group(BACKUP, BACKUP_B, LIVE_A, LIVE_B))
        self.assertEqual(
            set(labels),
            {"docfolderbackup_vs_live", "internal_duplicate_in_live_tree",
             "internal_duplicate_within_backup"},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
