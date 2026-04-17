# SyncScrap

SyncScrap — event-driven платформа для скрапинга с упором на антибот, гибкие стратегии по доменам и независимые воркеры пайплайна.

## Архитектура

- `root/contracts/v1/` — единые Pydantic-контракты между API и воркерами.
- `root/apps/api/` — FastAPI для загрузки целей, постановки discovery-задач и поиска.
- `root/apps/workers/` — независимые воркеры `scheduler`, `scout`, `delta`, `hunter_playwright`, `normalize`, `embedding`, `observability`.
- `root/persistence/` — PostgreSQL, миграции, DAO и сервисы поиска.
- `root/shared/` — конфиг, брокер, HTTP policy, retry, Redis и общие утилиты.

Базовый ingestion flow:

`scheduler -> discovery_urls -> scout -> discovered_items -> delta -> extraction_urls -> hunter -> normalized_items -> normalize`

Векторный контур (`embedding` + `qdrant`) опционален и не нужен для базового ingestion.

## Принципы

- Без отдельного агентного или промежуточного orchestration-слоя в рантайме.
- Ядро не должно зависеть от одного домена.
- Доменные HTTP-профили, discovery-стратегии и browser-сценарии подключаются через реестры.
- Антибот-логика живет в переиспользуемом слое (`http_policy`, retry, browser scenarios), а не размазывается по воркерам.

## Запуск

1. Создай `.env` рядом с `docker-compose.yaml`.
2. Подними базовый стек:

```bash
docker compose up -d --build
```

3. Если нужен векторный контур, включай профиль:

```bash
docker compose --profile vector up -d --build
```

## Масштабирование

- Воркеры можно масштабировать независимо друг от друга.
- Основные точки расширения: `scout` strategies, HTTP profiles, Playwright scenarios.
- Основной bottleneck проекта — антибот и качество доменных стратегий, а не структура репозитория.