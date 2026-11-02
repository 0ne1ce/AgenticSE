# C. CI на GitHub Actions

- **Ветка:** `task/c-ci`
- **Зависимости:** нет

## Цель

На каждый push и PR в `main` автоматически запускаются тесты и линтер.

## Требования

1. Файл `.github/workflows/ci.yml` с двумя jobs:
   - `tests` — матрица Python 3.11, 3.12 и 3.13, команда `python -m unittest discover -s tests -v`;
   - `lint` — `ruff check .` и `ruff format --check .`; ruff ставится через pip с зафиксированной версией.
2. Триггеры: push в `main` и pull_request в `main`.
3. Без секретов и сторонних сервисов. Разрешены только официальные `actions/checkout` и `actions/setup-python` с зафиксированной мажорной версией.

## Владение файлами

Только `.github/workflows/ci.yml`. Код, тесты, `ruff.toml` и README не менять.

## Приёмка

- Команды из workflow локально проходят на текущем `main`.
- Ревьюер проверяет структуру workflow: триггеры, матрицу, версии actions.
- Зелёный прогон CI на PR появится только после публикации. Это отдельный этап, он не входит в техническую готовность.

## Вне scope

Публикация пакета, покрытие, бейджи, pre-commit.
