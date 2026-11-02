"""Нормализация строковых значений JSON через командную строку."""

import argparse
import json
import sys
from pathlib import Path

from textkit import normalize_text


def _normalize_values(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [_normalize_values(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_values(item) for key, item in value.items()}
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, metavar="INPUT", help="входной JSON-файл")
    parser.add_argument("-o", type=Path, metavar="OUTPUT", help="выходной JSON-файл")
    arguments = parser.parse_args()

    try:
        value = json.loads(arguments.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Ошибка чтения {arguments.input}: {error}", file=sys.stderr)
        return 1

    result = json.dumps(_normalize_values(value), ensure_ascii=False, indent=2) + "\n"
    if arguments.o is None:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(result)
    else:
        arguments.o.write_text(result, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
