# textkit-demo

Учебная библиотека для работы с текстом на стандартной библиотеке Python. Сделана для демо доклада «Агенты ИИ в разработке ПО»: на ней агентный workflow Galaxy / Universe выполняет эпик из трёх задач.

| Задача | Что делает | Зависимости |
| --- | --- | --- |
| [A](tasks/A-normalize/TASK.md) | `normalize_text`: Unicode-нормализация и пробелы | — |
| [B](tasks/B-jsonnorm/TASK.md) | `python -m textkit.jsonnorm`: нормализация строк в JSON | A смёржена |
| [C](tasks/C-ci/TASK.md) | CI на GitHub Actions: тесты и линтер | — |

A и C независимы и идут первой волной, каждая в своём worktree. B стартует после merge A.

## Проверки

```sh
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Правила для агентов — в [AGENTS.md](AGENTS.md).
