import unittest

from textkit import normalize_text


class NormalizeTextTest(unittest.TestCase):
    def test_canonical_equivalents_have_same_composed_result(self) -> None:
        for text in ("é", "e\u0301"):
            with self.subTest(text=text):
                self.assertEqual(normalize_text(text), "é")

    def test_compatibility_distinctions_are_preserved(self) -> None:
        for text, other in (("ﬁ", "fi"), ("Ａ", "A"), ("x²", "x2")):
            with self.subTest(text=text):
                self.assertEqual(normalize_text(text), text)
                self.assertNotEqual(normalize_text(text), normalize_text(other))

    def test_whitespace_runs_collapse_and_edges_disappear(self) -> None:
        text = " \t\n\r\u00a0Alpha \t\n\r\u00a0\u2003\u202f\u3000\x1c Beta\u3000\t "
        self.assertEqual(normalize_text(text), "Alpha Beta")

    def test_empty_and_whitespace_only_inputs_become_empty(self) -> None:
        for text in ("", " \t\n\r\u00a0\u2003\u202f\u3000\x1c"):
            with self.subTest(text=text):
                self.assertEqual(normalize_text(text), "")

    def test_case_is_preserved(self) -> None:
        self.assertEqual(normalize_text("MiXeD Éé"), "MiXeD Éé")
        self.assertNotEqual(normalize_text("A"), normalize_text("a"))

    def test_ordinary_text_is_preserved(self) -> None:
        text = "Привет, мир! Hello — 42 🙂"
        self.assertEqual(normalize_text(text), text)

    def test_non_whitespace_and_unusual_string_values_are_preserved(self) -> None:
        for text in ("a\u200bb\ufeffc", "a\x00b", "\u0301", "\u0378", "\ud800"):
            with self.subTest(text=repr(text)):
                self.assertEqual(normalize_text(text), text)

    def test_repeated_normalization_is_stable(self) -> None:
        for text, expected in ((" \te\u0301\n Ａ x² ", "é Ａ x²"), ("", "")):
            with self.subTest(text=text):
                self.assertEqual(normalize_text(normalize_text(text)), expected)


if __name__ == "__main__":
    unittest.main()
