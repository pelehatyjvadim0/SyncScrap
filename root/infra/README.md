# Инфраструктура и оркестрация

- Docker Compose в корне репозитория: `docker-compose.yaml` (контекст сборки - весь проект).
- Сервисы пайплайна: api, scout, delta, hunter (playwright), normalize, embedding, observability, scheduler.
- Переменные окружения: `.env` рядом с compose.

Структура кода относительно этого файла:

- `root/contracts/v1/` - контракты сообщений
- `root/apps/` - HTTP API и воркеры
- `root/persistence/` - БД, миграции
- `root/shared/` - конфиг, брокер, redis, утилиты
