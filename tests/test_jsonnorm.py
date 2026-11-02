import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class JsonNormCliTest(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.input_path = self.directory / "input.json"
        self.output_path = self.directory / "output.json"

    def write_input(self, value: object) -> None:
        self.input_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def run_cli(self, *arguments: str, env: dict[str, str] | None = None):
        return subprocess.run(
            [sys.executable, "-m", "textkit.jsonnorm", *arguments],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            env=env,
            timeout=10,
            check=False,
        )

    def assert_success(self, result) -> None:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")

    def assert_input_error(self, result) -> None:
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.strip())
        self.assertIn(str(self.input_path).encode(), result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_nested_strings_normalize_and_other_values_preserve_type(self) -> None:
        self.write_input(
            {
                "items": [" \te\u0301\n ", {"value": " A\u00a0 B "}, [" Ａ x² "]],
                "scalars": [42, 1.5, True, False, None],
            }
        )
        result = self.run_cli(str(self.input_path))
        self.assert_success(result)
        value = json.loads(result.stdout)
        self.assertEqual(value["items"], ["é", {"value": "A B"}, ["Ａ x²"]])
        self.assertEqual(value["scalars"], [42, 1.5, True, False, None])
        self.assertEqual(
            [type(item) for item in value["scalars"]], [int, float, bool, bool, type(None)]
        )

    def test_keys_and_their_order_stay_unchanged_at_each_depth(self) -> None:
        self.write_input({" z ": {"e\u0301": " x ", "é": " y "}, "a": " z "})
        result = self.run_cli(str(self.input_path))
        self.assert_success(result)
        value = json.loads(result.stdout)
        self.assertEqual(list(value), [" z ", "a"])
        self.assertEqual(list(value[" z "]), ["e\u0301", "é"])
        self.assertEqual(value, {" z ": {"e\u0301": "x", "é": "y"}, "a": "z"})

    def test_all_root_types_are_supported(self) -> None:
        cases = [
            (" \te\u0301\n ", "é"),
            ([" x ", {"nested": " y "}], ["x", {"nested": "y"}]),
            ({}, {}),
            ([], []),
            (7, 7),
            (2.5, 2.5),
            (True, True),
            (False, False),
            (None, None),
            (" \t ", ""),
        ]
        for original, expected in cases:
            with self.subTest(original=original):
                self.write_input(original)
                result = self.run_cli(str(self.input_path))
                self.assert_success(result)
                actual = json.loads(result.stdout)
                self.assertEqual(actual, expected)
                self.assertIs(type(actual), type(expected))

    def test_stdout_uses_utf8_and_two_space_indentation(self) -> None:
        self.write_input({"message": [" Привет 🙂 ", " e\u0301 "]})
        result = self.run_cli(str(self.input_path))
        self.assert_success(result)
        expected = '{\n  "message": [\n    "Привет 🙂",\n    "é"\n  ]\n}\n'
        self.assertEqual(result.stdout, expected.encode("utf-8"))

    def test_stdout_is_utf8_even_when_pythonioencoding_is_ascii(self) -> None:
        self.write_input(" Привет e\u0301 🙂 ")
        env = os.environ.copy()
        env.update(PYTHONIOENCODING="ascii", PYTHONUTF8="0", LC_ALL="C")
        result = self.run_cli(str(self.input_path), env=env)
        self.assert_success(result)
        self.assertEqual(result.stdout, '"Привет é 🙂"\n'.encode())

    def test_output_file_uses_utf8_and_leaves_stdout_empty(self) -> None:
        self.write_input({"name": " Привет e\u0301 🙂 "})
        self.output_path.write_text("previous output", encoding="utf-8")
        result = self.run_cli(str(self.input_path), "-o", str(self.output_path))
        self.assert_success(result)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(self.output_path.read_bytes(), '{\n  "name": "Привет é 🙂"\n}\n'.encode())

    def test_input_can_also_be_the_output_file(self) -> None:
        self.write_input({"value": " e\u0301 "})
        result = self.run_cli(str(self.input_path), "-o", str(self.input_path))
        self.assert_success(result)
        self.assertEqual(json.loads(self.input_path.read_bytes()), {"value": "é"})

    def test_missing_input_reports_error_without_creating_output(self) -> None:
        result = self.run_cli(str(self.input_path), "-o", str(self.output_path))
        self.assert_input_error(result)
        self.assertFalse(self.output_path.exists())

    def test_invalid_json_reports_error_and_preserves_existing_output(self) -> None:
        self.input_path.write_text('{"broken":', encoding="utf-8")
        self.output_path.write_bytes(b"previous output")
        result = self.run_cli(str(self.input_path), "-o", str(self.output_path))
        self.assert_input_error(result)
        self.assertEqual(self.output_path.read_bytes(), b"previous output")

    def test_argument_errors_use_argparse_exit_code(self) -> None:
        for arguments in ((), ("--unknown",), (str(self.input_path), "-o")):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"usage:", result.stderr)
                self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
