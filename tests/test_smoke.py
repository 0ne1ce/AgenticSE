import unittest

import textkit


class SmokeTest(unittest.TestCase):
    def test_package_has_version(self) -> None:
        self.assertEqual(textkit.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
