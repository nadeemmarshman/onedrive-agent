"""
Phase 5 live test runner.

Wires the full Phase 1-5 chain together for a demo run against
the sample folder -- no API calls needed for this test, since
we're testing the approval gate itself, not the decision loop.

Flow:
  1. Scan the sample folder (Phase 1)
  2. Find duplicates + convertible files (Phase 1)
  3. Propose actions (Phase 1)
  4. Run the approval gate (Phase 5):
     a. Write pre_run_snapshot.json
     b. Present full proposal list
     c. Collect per-item approvals
     d. Execute approved actions

Run from C:\\Dev\\onedrive-agent:
  python test_phase5_live.py

NOTE: this WILL delete files if you approve deletions.
The sample_data/ folder is disposable test data, but be
aware that approving actions here causes real file changes.
Pre-run snapshot is written to pre_run_snapshot.json before
anything executes -- check that file to see what existed before.
"""

from tools import scan_folder, find_duplicates, find_convertible_files, propose_action
from approval_gate import run_approval_gate

if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# PHASE 5 LIVE TEST — end-to-end approval gate demo")
    print("# Target: sample_data/")
    print("#" * 60)

    # Phase 1: scan, detect, propose
    print("\nScanning sample_data/...")
    files = scan_folder("sample_data", recursive=True)
    print(f"Found {len(files)} file(s)")

    dup_groups   = find_duplicates(files)
    convertible  = find_convertible_files(files)
    proposals    = propose_action(dup_groups, convertible)

    print(f"Duplicates: {len(dup_groups)} group(s)")
    print(f"Convertible: {len(convertible)} file(s)")
    print(f"Proposals: {len(proposals)}")

    if not proposals:
        print("\nNo proposals generated -- nothing to approve.")
    else:
        # Phase 5: approval gate
        result = run_approval_gate(proposals)
        print(f"\nFinal result: {result}")
