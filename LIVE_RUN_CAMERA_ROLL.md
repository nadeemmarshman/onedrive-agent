# Live run report -- 2026-07-30

Target: OneDrive\Pictures\Camera Roll (path redacted to filename level below)
Files scanned: 218
Duplicate groups (identical content, MD5): 2
Redundant files: 2
Reclaimable space: 5.8 MB

## Groups
- ['IMG_20260326_123420 1.jpg', 'IMG_20260326_123420.jpg']
- ['IMG_20260713_153505 1.jpg', 'IMG_20260713_153505.jpg']

## Finding: keeper selection in `propose_action()`

`propose_action()` (Phase 1, `tools.py`) keeps `group[0]` as the "original"
arbitrarily and proposes deleting the rest. Both groups here follow
OneDrive's own sync-conflict naming convention -- a " 1" suffix before the
extension marks the copy OneDrive created on a naming conflict, not the
original -- and in both cases `group[0]` happened to be the suffixed
(conflict-copy) file, i.e. the reverse of the intended keep/delete choice.

Not fixed in `tools.py` itself (out of scope for this exercise -- would
change Phase 1 behaviour retroactively). Instead, `propose_camera_roll_dedup.py`
reorders each group so a plain-named file is preferred as keeper before
calling `propose_action()`. See `PROPOSED_ACTIONS_CAMERA_ROLL.json` for the
resulting proposal -- for human review only, nothing deleted.

