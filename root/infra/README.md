# Инфраструктура и оркестрация

- Docker Compose в корне репозитория: `docker-compose.yaml` (контекст сборки - весь проект).
- Сервисы MAS: api, scout, delta, hunter (playwright), normalize, embedding, observability, scheduler.
- Переменные окружения: `.env` рядом с compose.

Структура кода относительно этого файла:

- `root/contracts/v1/` - контракты сообщений
- `root/apps/` - HTTP API, оркестратор, воркеры
- `root/mcp_servers/` - заготовки MCP (реализация позже)
- `root/persistence/` - БД, миграции
- `root/shared/` - конфиг, брокер, redis, утилиты
