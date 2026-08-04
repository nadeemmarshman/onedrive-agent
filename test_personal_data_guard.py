r"""
Tests for the pre-commit personal-data guard (check_staged_for_personal_data.py).

These exist because the guard is the control that replaced human vigilance
after the same mistake recurred three times during the RAID I27
remediation. A control that silently stops working is worse than no
control, since it invites the confidence without the protection.

Layer 2 (structural) is the one that matters most and is tested hardest:
it is the only layer that can catch a term nobody thought to add to the
mapping. Its first implementation excluded whitespace from path segments
and therefore missed any folder name containing a space -- i.e. exactly
the realistic case. `test_structural_catches_unmapped_path_with_spaces`
pins that regression.
"""

import re
import unittest

from check_staged_for_personal_data import PLACEHOLDER, STRUCTURAL, _mask_placeholders


# A 13-digit value that is deliberately NOT a valid identity number.
# Asserted against the checksum in the test below, so this file can never
# drift back to carrying a real-shaped ID.
NOT_AN_ID = "1" * 13


def _luhn_valid(number: str) -> bool:
    """Luhn check digit, as used by South African ID numbers."""
    total, alternate = 0, False
    for char in reversed(number):
        digit = int(char)
        if alternate:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        alternate = not alternate
    return total % 10 == 0


def structural_hit(text: str) -> str | None:
    """Return the reason a line trips the structural layer, else None."""
    for pattern, why in STRUCTURAL:
        m = pattern.search(text)
        if m and not PLACEHOLDER.search(m.group(0)):
            return why
    return None


class TestStructuralLayer(unittest.TestCase):
    """Shape-based detection, independent of any curated token list."""

    def test_structural_catches_unmapped_path_with_spaces(self):
        # Regression: folder names contain spaces. An earlier pattern
        # excluded whitespace and missed this entirely.
        line = r"| 2.1 MB | `00-My Folders\Some Unmapped Folder\Another Level\Thing_2019.pdf` |"
        self.assertEqual(structural_hit(line),
                         "deep path chain ending in a document filename")

    def test_structural_catches_user_profile_path(self):
        line = r"see C:\Users\SomeUser\OneDrive\whatever for detail"
        self.assertEqual(structural_hit(line),
                         "absolute path under a user profile")

    def test_structural_catches_long_digit_run(self):
        # Fixture must be 13 digits so the pattern fires, but MUST NOT be a
        # valid identity number. South African IDs carry a Luhn check digit,
        # so a "realistic-looking" fixture can be a structurally valid ID --
        # i.e. potentially a real person's, even when invented at random.
        # The original fixture here was exactly that mistake: made up to look
        # plausible, and it passed the Luhn check. Found by an independent
        # audit, not by the author. All-ones fails the checksum and is
        # obviously synthetic to a reader.
        self.assertFalse(_luhn_valid(NOT_AN_ID), "fixture must not be a valid ID number")
        self.assertEqual(structural_hit(f"Reference {NOT_AN_ID} on the form."),
                         "long digit run (possible identity/reference number)")

    def test_structural_ignores_placeholder_paths(self):
        # Sanitised output must not trip the guard, or the guard becomes
        # noise and gets overridden habitually.
        line = r"Kept `{{identity-documents}}\{{file}}.jpg` and `{{hobby-records}}\{{sub}}\{{f}}.pdf`"
        self.assertIsNone(structural_hit(line))

    def test_structural_ignores_ordinary_prose(self):
        for line in [
            "Resolved 7 internal-duplicate groups, 9.37 MB reclaimed.",
            "See LIVE_RUN_PCBACKUP.md and analyze_pcbackup_delta.py for detail.",
            "The scan found 948 duplicate groups across 3,084 files.",
            "Run `git config core.hooksPath .githooks` once per clone.",
        ]:
            with self.subTest(line=line):
                self.assertIsNone(structural_hit(line))

    def test_structural_ignores_short_relative_code_paths(self):
        # Two-segment repo-relative paths are normal in docs and must pass.
        self.assertIsNone(structural_hit("edit Handoff-Briefs/Live-Run-Handoff_v1.0.md"))


class TestPlaceholderPattern(unittest.TestCase):
    def test_matches_generated_placeholders(self):
        for p in ["{{identity-documents}}", "{{employerA}}", "{{hobby-records}}", "{{DOCS_ROOT}}"]:
            with self.subTest(p=p):
                self.assertIsNotNone(PLACEHOLDER.search(p))

    def test_does_not_match_ordinary_brace_usage(self):
        self.assertIsNone(PLACEHOLDER.search("a dict literal like {a: 1, b: 2}"))

    def test_does_not_match_markdown_link_text(self):
        # The reason {{...}} was chosen over [...]: a single-word markdown
        # link like [here](url) would match a square-bracket placeholder
        # regex and get masked as "already redacted" by _mask_placeholders,
        # which could hide a genuine leaked token inside real link text.
        self.assertIsNone(PLACEHOLDER.search("see [here](https://example.com) for detail"))


def _token_hits(text: str, tokens: list[str]) -> list[str]:
    """Reproduce main()'s Layer 1 matching against masked text, without
    depending on the real (gitignored) mapping file, so this test runs on
    any clone."""
    masked = _mask_placeholders(text)
    return [t for t in tokens if t.lower() in masked.lower()]


class TestLayer1PlaceholderMasking(unittest.TestCase):
    """Regression: Layer 1 matched tokens against the RAW line, so a
    mapped token that is only a substring of an already-correct
    placeholder still fired. Same ambiguous-substring class as the
    documented "Bytes" -> size_bytes incident, rediscovered independently
    by Cowork's v1.1 finding: a real, correctly-mapped, ordinary-English-
    word token (a sensitive folder name) matched inside its own correctly
    -generated placeholder in an otherwise fully sanitised document.

    Fixture below uses a synthetic token/placeholder pair rather than the
    real one, deliberately, per this file's own header: writing about a
    leak by quoting it is the exact pattern this whole guard exists to
    prevent, and it has already recurred more than once in this repo.
    """

    FIXTURE_TOKEN = "Zephyr"
    FIXTURE_PLACEHOLDER = "{{zephyr-records}}"

    def test_token_inside_an_existing_placeholder_does_not_fire(self):
        line = f"remainder -- ShareX\\Backup\\ configs, `{self.FIXTURE_PLACEHOLDER}\\`, Unsorted\\"
        self.assertEqual(_token_hits(line, [self.FIXTURE_TOKEN]), [])

    def test_same_token_still_fires_on_a_genuine_leak(self):
        line = f"the file lives in the {self.FIXTURE_TOKEN} folder under 00-My Folders"
        self.assertEqual(_token_hits(line, [self.FIXTURE_TOKEN]), [self.FIXTURE_TOKEN])

    def test_masking_preserves_line_length_and_non_placeholder_content(self):
        line = "before {{a-placeholder}} after"
        masked = _mask_placeholders(line)
        self.assertEqual(len(masked), len(line))
        self.assertTrue(masked.startswith("before "))
        self.assertTrue(masked.endswith(" after"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
