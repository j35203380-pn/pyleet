

# ⚡ Pyleet

### Асинхронная платформа для решения задач по программированию с изолированным выполнением кода


**Pet-project в духе LeetCode:** задачи, решения, комментарии, категории, JWT-авторизация,
кэш, rate limiting — и главное: **безопасное выполнение пользовательского кода
в отдельном микросервисе через RabbitMQ + Docker-sandbox** с применением паттернов
**Transactional Outbox / Inbox**.



---

## 📖 Содержание

- [🧠 О проекте](#-о-проекте)
- [✨ Ключевые возможности](#-ключевые-возможности)
- [🏗 Архитектура](#-архитектура)
- [🔄 Жизненный цикл решения](#-жизненный-цикл-решения)
- [📬 Transactional Outbox / Inbox](#-transactional-outbox--inbox)
- [🛠 Технологический стек](#-технологический-стек)
- [📁 Структура проекта](#-структура-проекта)
- [🚀 Быстрый старт (Docker Compose)](#-быстрый-старт-docker-compose)
- [🧑‍💻 Запуск без Docker](#-запуск-без-docker)
- [📡 API Reference](#-api-reference)
- [🖥 Админ-панель](#-админ-панель)
- [🐳 Code Sandbox](#-code-sandbox)
- [⚙️ Workers](#️-workers)
- [🔴 Redis в проекте](#-redis-в-проекте)
- [🐘 База данных](#-база-данных)
- [🧪 Тестирование](#-тестирование)
- [📈 Нагрузочное тестирование](#-нагрузочное-тестирование)
- [🗺 Roadmap](#-roadmap)
- [⚠️ Статус проекта и замечания](#️-статус-проекта-и-замечания)

---

## 🧠 О проекте

**Pyleet** — backend-платформа для решения алгоритмических задач с автоматической проверкой кода.

Главная идея — пользовательский код **никогда не выполняется внутри API-приложения**.
Вместо этого система разбита на независимые сервисы, общающиеся через RabbitMQ:

```text
┌────────────────────────┐        ┌──────────────────────────┐
│   🌐 Main Application  │        │      ⚙️ Workers           │
│   FastAPI + Granian    │        │   FastStream             │
│                        │        │                          │
│  • auth (JWT RS256)    │        │  • Outbox Relay          │
│  • tasks / categories  │        │  • Inbox Relay           │
│  • submissions         │        │  • Clear (cron)          │
│  • comments            │        │                          │
│  • SQLAdmin panel      │        └───────────┬──────────────┘
└───────────┬────────────┘                    │
            │                                 │
            ▼                                 ▼
   ┌────────────────────────────────────────────────────┐
   │              🐇 RabbitMQ (exchange: submission)    │
   │        solution.execute  ←→  solution.result       │
   └───────────────────────┬────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   🧪 Code Isolator     │
              │   FastStream + aiodocker│
              │                        │
              │   🐳 Docker Sandbox    │
              │   (net off, ro fs,     │
              │    128MB, 0.5 CPU)     │
              └────────────────────────┘
```

Весь стек — **полностью асинхронный**: FastAPI, SQLAlchemy 2.0 async + asyncpg,
redis.asyncio, FastStream/RabbitMQ, aiodocker. Блокирующие операции (Argon2, JWT)
вынесены в `asyncio.to_thread`, нагрузка на БД и брокер ограничена семафорами.

---

## ✨ Ключевые возможности

| Возможность | Реализация |
|---|---|
| 🔐 Аутентификация | JWT **RS256** (приватный/публичный ключ), access-token 30 минут, OAuth2 Bearer |
| 🔑 Пароли | Хеширование **Argon2** (`argon2-cffi`), валидация и подтверждение пароля |
| 🚫 Blacklist токенов | Механизм logout через Redis `black_list:{jti}` с TTL до конца жизни токена |
| 🧩 Задачи | Сложность `EASY / MEDIUM / HARD`, starter code, `method_name`, тесты в JSONB |
| 📚 Категории | Many-to-many `type_tasks`, выдача задач по категориям |
| 📝 Submissions | UUID-идентификаторы, статусы жизненного цикла, exit code, output, time_ms |
| 🧪 Выполнение кода | Отдельный микросервис, Docker-sandbox с жёсткими лимитами |
| 📬 Надёжная доставка | **Transactional Outbox** (гарантия публикации) + **Inbox** (идемпотентность обработки) |
| ⏱ Повторы с backoff | Экспоненциальный backoff `min(2ⁿ, 60)` c, до 5 попыток, отметка `failed_at` |
| 🧹 Очистка по расписанию | taskiq-scheduler, cron `0 */2 * * *` — удаление обработанных записей старше 24ч |
| ⚡ Кэш | Redis-кэш задач/категорий с **jitter TTL ±3с** и **distributed lock** от cache stampede |
| 🚦 Rate limiting | Sliding window на Redis ZSET (5 запросов / 5 секунд на IP+endpoint)* |
| 💬 Комментарии | CRUD + пагинация (`limit`/`offset`), чужие комментарии защищены фильтром по `user_id` |
| 📡 Доставка результата | Redis **Pub/Sub** + кэш результата (TTL 90с) — клиент получает verdict без поллинга |
| 🖥 Админка | **SQLAdmin** для управления задачами и категориями |
| 🧵 Сериализация | **msgspec** (`Struct`) для быстрых сообщений брокера, pydantic v2 для API |
| 🧪 Тесты | pytest + httpx `ASGITransport` (без сети), сценарии на все эндпоинты |
| 📈 Нагрузка | Locust-сценарий: регистрация → логин → submit → result |
| 🐳 Инфраструктура | Полный `compose.yaml`: PostgreSQL 18, Redis 7, RabbitMQ 3, API, workers, scheduler, sandbox |

<sub>*Middleware rate limiter реализован, но на данном этапе отключён (закомментирован в `main.py`).</sub>

---

## 🏗 Архитектура

Система состоит из **4 исполняемых компонентов** и **3 инфраструктурных сервисов**:

### Компоненты

| Компонент | Технология | Команда запуска | Зона ответственности |
|---|---|---|---|
| 🌐 **API** | FastAPI + Granian (ASGI) | `granian --interface asgi app.main:app --port 8001` | HTTP API, авторизация, кэш, публикация run-задач, запись outbox |
| ⚙️ **Workers** | FastStream | `faststream run workers.main:app` | Outbox Relay → RabbitMQ; Inbox Relay ← RabbitMQ → PostgreSQL |
| ⏰ **Scheduler** | taskiq + taskiq-faststream | `taskiq scheduler workers.sheduler:schedule` | Cron-задача очистки outbox/inbox каждые 2 часа |
| 🧪 **Code Isolator** | FastStream + aiodocker | `faststream run main:app` | Выполнение кода в sandbox, определение статуса, публикация результата |

### Инфраструктура

| Сервис | Образ | Назначение |
|---|---|---|
| 🐘 PostgreSQL | `postgres:18` | Основное хранилище (users, tasks, submissions, comments, outbox/inbox) |
| 🔴 Redis | `redis:7.0.15` | Кэш, Pub/Sub, rate limit, blacklist токенов, хранение результатов |
| 🐇 RabbitMQ | `rabbitmq:3-management-alpine` | Обмен сообщениями (AMQP, внешние порты `5673` / UI `15672`) |

### Топология RabbitMQ

```text
Exchange: submission
├── Queue: solution.execute   →  слушает Code Isolator      (job на выполнение)
└── Queue: solution.result    →  слушает Inbox Relay        (результат submit'а)

Exchange: outbox_inbox
└── Queue: clear              →  слушает clear_db worker    (cron через taskiq)
```

Каждое сообщение несёт `correlation_id = submission_id` — по нему результат
находит свою запись в БД, а клиент — свой ответ в Redis.

---

## 🔄 Жизненный цикл решения

В API предусмотрены **два режима** проверки кода.

### ▶️ `run` — быстрая проверка (без записи в БД)

```text
👨‍💻 Client
   │ POST /solution/run/{task_id}   { "code": "class Solution: ..." }
   ▼
🌐 FastAPI ──(кэш задачи: Redis → lock → PostgreSQL)──► ExecutionReq (msgspec)
   │
   │ broker.publish(queue=solution.execute, correlation_id=submission_id)
   ▼
🧪 Code Isolator ──► 🐳 Docker Sandbox ──► CodeRunner ──► verdict
   │
   ├──► 🔴 Redis:  SET result:submission:{id} (TTL 90s)
   └──► 🔴 Redis:  PUBLISH result:submission:{id}
   ▲
👨‍💻 Client ── GET /solution/result/{submission_id}
              (сначала GET из Redis, затем Pub/Sub c ожиданием 3с,
               иначе повторный GET, иначе {"status": "timeout"})
```

### ✅ `submit` — официальная посылка (с персистентностью)

```text
👨‍💻 Client ── POST /solution/submit/{task_id}
   ▼
🌐 FastAPI: в ОДНОЙ транзакции PostgreSQL
   ├── INSERT submissions   (id=UUID, status=pending)
   └── INSERT outboxsub     (message=ExecutionReq)
   ▼                     ↩️ HTTP-ответ сразу: {id, status, created_at}
   ▼
⚙️ Outbox Relay (workers): poll БД → publish в solution.execute
   ▼
🧪 Code Isolator: sandbox → verdict → т.к. mode=submit:
   ├──► 🐇 RabbitMQ: solution.result
   ├──► 🔴 Redis SET + PUBLISH (для /solution/result)
   ▼
⚙️ Inbox Relay (workers): batch-приём, дедупликация через inboxsub,
   UPDATE submissions (status, exit_code, output, time_ms), ACK
   ▼
🧹 Scheduler (cron 0 */2 * * *): очистка inboxsub/outboxsub старше 24ч
```

---

## 📬 Transactional Outbox / Inbox

Это ядро надёжности messaging-слоя:

### 📤 Outbox (`workers/outbox/outbox_relay.py`)

- API **не публикует** в RabbitMQ при submit'е — запись `Submission` + `OutboxSub`
  создаются атомарно в одной транзакции. Даже если брокер недоступен — сообщение не потеряется.
- Relay забирает строки батчами по 20 с `SELECT ... FOR UPDATE SKIP LOCKED`
  (безопасно для нескольких инстансов воркера).
- Публикация через `asyncio.TaskGroup` под семафором (50 одновременных),
  с таймаутом 10с на publish.
- При ошибке: `count += 1`, сохраняется `last_error`, повтор через
  **экспоненциальный backoff** `min(2^count, 60)` секунд; после 5 неудач — `failed_at` (dead).
- Адаптивный polling: 0.2с при полной пачке, 5с при пустой БД.

### 📥 Inbox (`workers/inbox/inbox_relay.py`)

- Подписка на `solution.result` с `prefetch_count=50` и `AckPolicy.NACK_ON_ERROR`.
- Сообщения складываются в `asyncio.Queue` и разбираются **батчами до 40** (ожидание 1с).
- Перед записью проверяется `inboxsub` — **дедупликация**: уже обработанные
  `submission_id` просто подтверждаются (ACK) без повторного UPDATE.
- Массовый `UPDATE submissions` + `INSERT inboxsub` одной транзакцией, затем ACK.
- `IntegrityError` при гонке конкурентных воркеров перехватывается и логируется.

```text
   🌐 API                    🐇 RabbitMQ                ⚙️ Workers
┌──────────────┐         ┌─────────────────┐        ┌──────────────────┐
│ TX:          │         │ solution.execute│        │ Outbox Relay     │
│ submissions  │──row──► │                 │──msg──►│ (retry/backoff)  │
│ + outboxsub  │         │ solution.result │        │ Inbox Relay      │
└──────────────┘         └─────────────────┘        │ (batch + dedup)  │
        ▲                                            └────────┬─────────┘
        └──────────── UPDATE submissions ◄────────────────────┘
```

---

## 🛠 Технологический стек

| Слой | Технологии |
|---|---|
| **Web** | FastAPI, Granian (production ASGI-server), Uvicorn (dev), Starlette |
| **Валидация** | Pydantic v2, pydantic-settings, msgspec (брокерные сообщения) |
| **БД** | PostgreSQL 18, SQLAlchemy 2.0 (async), asyncpg, Alembic (async migrations) |
| **Кэш / realtime** | Redis 7 (redis.asyncio): cache, locks, Pub/Sub, rate limit, blacklist |
| **Брокер** | RabbitMQ 3, FastStream, aio-pika |
| **Scheduling** | taskiq, taskiq-faststream (cron), pycron |
| **Безопасность** | PyJWT (RS256), argon2-cffi, OAuth2PasswordBearer, Docker-изоляция |
| **Изоляция кода** | aiodocker (Docker Engine API), контейнер `python:3.11-slim` |
| **Админка** | SQLAdmin |
| **Тесты** | pytest, pytest-asyncio, httpx (ASGITransport), asgi-lifespan, Locust |
| **Профилирование** | py-spy (в зависимостях backend) |
| **Контейнеризация** | Docker, Docker Compose (healthchecks, depends_on conditions) |

---

## 📁 Структура проекта

```text
pyleet/
├── compose.yaml                        # 🐳 Вся инфраструктура + 4 сервиса приложения
├── .gitignore                          # *.pem, .env, venv, __pycache__, *.db ...
│
├── beckend/                            # 🌐 Main Application + ⚙️ Workers
│   ├── Dockerfile                      # python:3.12.3-slim (без CMD — команда в compose)
│   ├── requirements.txt                # Пиннованные зависимости API/воркеров
│   ├── config.py                       # ⚙️ Settings (pydantic-settings), enum'ы статусов
│   ├── alembic.ini                     # Конфиг Alembic
│   ├── locustfile.py                   # 📈 Нагрузочный сценарий (reg→login→submit→result)
│   ├── script_tatsk_add.py             # 🧩 Сид-скрипт: задача "Two Sum II" + категория
│   │
│   ├── alembic/                        # 🔄 Миграции (async env.py)
│   │   ├── env.py                      # async-миграции, URL из settings
│   │   ├── script.py.mako
│   │   └── versions/                   # 9 ревизий (см. раздел «База данных»)
│   │
│   ├── app/
│   │   ├── main.py                     # FastAPI app: lifespan (Redis pool), роутеры,
│   │   │                               #   exception handler, SQLAdmin, rate-limit middleware*
│   │   ├── dependcies.py               # CurUs (текущий юзер), ReschePoints (заготовка ролей)
│   │   ├── exceptions.py               # Доменные исключения (TaskNotFound, UserNotFound, ...)
│   │   │
│   │   ├── Admin/
│   │   │   └── models.py               # 🖥 SQLAdmin: Auth backend + ModelView Task/Category
│   │   │
│   │   ├── auth/
│   │   │   ├── auth.py                 # Argon2, JWT RS256 (encode/decode в to_thread),
│   │   │   │                           #   current_token (blacklist, type=access), logout
│   │   │   ├── login.py                # Роуты /auth: регистрация, login, me
│   │   │   └── repositories.py         # UserAdd / UserLogin (семафор 20)
│   │   │
│   │   ├── database/
│   │   │   ├── db.py                   # async engine (pool 20+20), sessionmaker, get_db
│   │   │   ├── models/
│   │   │   │   ├── auth_models.py      # User
│   │   │   │   └── task_models.py      # Task, Comments, Submission, Category,
│   │   │   │                           #   TypeTask, OutboxSub, InboxSub, comments_count
│   │   │   └── shemas/
│   │   │       ├── auth_shemas.py      # UserPost (валидаторы), Token, ...
│   │   │       └── task_shemas.py      # DTO задач/комментов/submissions/execution
│   │   │
│   │   ├── redis_client/
│   │   │   ├── redis_connect.py        # Depends: redis из app.state
│   │   │   ├── redis_cache.py          # RedisCache: get/set/list, jitter TTL, locks,
│   │   │   │                           #   batch-удаление по префиксу (SCAN+UNLINK)
│   │   │   ├── redis_limite.py         # RateLimite: sliding window (ZSET pipeline)
│   │   │   └── redis_raiting.py        # Raiting: ZINCRBY/ZREVRANGE (заготовка рейтинга)
│   │   │
│   │   └── routers/
│   │       ├── __init__.py             # Агрегирующий approuter
│   │       ├── get_task.py             # /problems — задачи + кэш с lock'ом
│   │       ├── category_task.py        # /category — категории + кэш
│   │       ├── coments_user.py         # /coments — CRUD комментариев (auth)
│   │       ├── solution_router.py      # /solution — run / submit / result (auth)
│   │       ├── service.py              # Сборка ExecutionReq из задачи и кода
│   │       └── repositories/           # Слой доступа к данным (Core-запросы SQLAlchemy)
│   │           ├── shemas.py           # msgspec Structs: ExecutionReq, SubmissCode
│   │           ├── task_rep.py         # GetTask, LevelTask
│   │           ├── submission_rep.py   # SubmissionPost: TX (submission + outbox)
│   │           ├── category_rep.py     # CategoriesGet (selectinload), CategoriesAll
│   │           └── comment_rep.py      # Add/Update/Del/Get/AllGet/TaskComments
│   │
│   ├── workers/                        # ⚙️ FastStream-воркеры
│   │   ├── main.py                     # FastStream app: lifespan запускает outbox+inbox
│   │   ├── connect_broker.py           # RabbitBroker + подключение роутеров
│   │   ├── shemas.py                   # msgspec: ExecutionResult, SubmissionUpdate
│   │   ├── outbox/outbox_relay.py      # 📤 Outbox: skip_locked, backoff, TaskGroup
│   │   ├── inbox/inbox_relay.py        # 📥 Inbox: батчи до 40, дедупликация, bulk update
│   │   ├── sheduler.py                 # ⏰ taskiq StreamScheduler (cron 0 */2 * * *)
│   │   └── clear_db.py                 # 🧹 Подписчик queue=clear: чистка >24ч
│   │
│   └── test_/                          # 🧪 pytest-тесты API
│       ├── conftest.py                 # Fixtures: client (ASGITransport), auth_client
│       ├── test_auth.py                # Регистрация
│       ├── test_task.py                # /problems
│       ├── test_category.py            # /category
│       ├── test_comm.py                # /coments (полный CRUD)
│       └── test_solution.py            # /solution run + submit + result
│
└── code_sandbox/                       # 🧪 Code Isolator (отдельный сервис)
    ├── Dockerfile                      # python:3.12.3-slim, CMD faststream run main:app
    ├── requirements.txt
    ├── config.py                       # Те же Settings (broker, redis)
    ├── shemas.py                       # ExecutionRequest/Result + ConfDcoker (лимиты)
    ├── main.py                         # FastStream app: aiodocker + redis pool в Context
    └── isolated/
        ├── subscribe.py                # 📥 solution.execute → isolate → publish
        ├── harness.py                  # Сборка скрипта: user code + CodeRunner + маркер
        ├── isolate.py                  # 🐳 create → attach stdin → start → wait/kill → parse
        ├── service.py                  # Определение статуса по exit_code/test_result
        └── publish.py                  # 📤 solution.result (семафор 50)
```


---

## 🚀 Быстрый старт (Docker Compose)

### 1. Клонирование

```bash
git clone https://github.com/j35203380-pn/pyleet.git
cd pyleet
```

### 2. Переменные окружения

Создай `.env` **в корне проекта** (используется и `compose.yaml`, и обоими приложениями):

```env
# ── PostgreSQL ─────────────────────────────
POSTGRES_HOST=db
POSTGRES_USER=pyleet
POSTGRES_PASSWORD=secret
POSTGRES_NAME=pyleet
POSTGRES_PORT=5432

# ── Redis ──────────────────────────────────
REDIS_HOST=redis
REDIS_USER=
REDIS_PORT=6379
REDIS_PASSWORD=

# ── RabbitMQ ───────────────────────────────
RBROKER_HOST=rabbitmq
RBROKER_USER=guest
RBROKER_PORT=5672
RBROKER_PASSWORD=guest

# ── JWT (пути к ключам от корня проекта) ───
JWT_SECRET_KEY=keys/private.pem
JWT_PUBLIC_KEY=keys/public.pem
ALGORITHM=RS256
```

| Переменная | Назначение |
|---|---|
| `POSTGRES_*` | Подключение к PostgreSQL (`DATABASE_URL` собирается как `postgresql+asyncpg://...`) |
| `REDIS_*` | Подключение к Redis (`redis://host:port`) |
| `RBROKER_*` | Подключение к RabbitMQ (`amqp://user:pass@host:port`) |
| `JWT_SECRET_KEY` / `JWT_PUBLIC_KEY` | **Пути** к приватному/публичному PEM-ключам |
| `ALGORITHM` | Алгоритм подписи JWT (`RS256`) |

> 💡 Значения выше — для запуска **внутри compose** (сервисы видят друг друга по именам).
> Для запуска приложений **на хосте** используй `localhost` и порт RabbitMQ `5673`
> (compose пробрасывает `5673:5672`).

### 3. JWT-ключи (RS256)

```bash
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

Ключи и `.env` игнорируются git'ом (`*.pem`, `.env` в `.gitignore`).

> ⚠️ В контейнерах путь разрешается от корня контейнера — при запуске `api`
> через compose примонтируй ключи, например добавь в сервис `api`:
> ```yaml
> volumes:
>   - ./keys:/keys:ro
> ```

### 4. Запуск

```bash
docker compose up -d --build
```

Compose поднимет **7 сервисов** (у всех инфраструктурных — healthchecks,
приложения стартуют только после `service_healthy`):

| Сервис | Что делает | Порт |
|---|---|---|
| `db` | PostgreSQL 18 (+ volume `pgdata`) | `${POSTGRES_PORT}:5432` |
| `redis` | Redis 7.0.15 (+ volume `redis-data`) | `${REDIS_PORT}:${REDIS_PORT}` |
| `rabbitmq` | RabbitMQ 3 + Management UI | `5673:5672`, UI `15672` |
| `api` | FastAPI на **Granian** | `8001:8001` |
| `faststream-workers` | Outbox + Inbox relay | — |
| `taskiq-sheduler` | Cron-планировщик очистки | — |
| `faststream-service` | Code Isolator (нужен Docker-сокет на хосте) | — |

После запуска:

```text
🌐 API        → http://localhost:8001
📚 Swagger    → http://localhost:8001/docs
📖 ReDoc      → http://localhost:8001/redoc
🖥 Админка    → http://localhost:8001/admin
🐇 RabbitMQ UI→ http://localhost:15672  (guest / guest)
```

### 5. Миграции

```bash
docker compose exec api alembic upgrade head
```

### 6. Первая задача

Задачи и категории создаются через админку `/admin` либо сид-скриптом:

```bash
docker compose exec api python script_tatsk_add.py
# добавит категорию "Two Sum" и задачу "Two Sum II" (MEDIUM, method: two_sum_sorted, 4 теста)
```

---

## 🧑‍💻 Запуск без Docker

```bash
# 1. Инфраструктура
docker compose up -d db redis rabbitmq

# 2. Виртуальное окружение (Python 3.12)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r beckend/requirements.txt

# 3. Миграции (из каталога beckend, .env — в корне)
cd beckend
alembic upgrade head

# 4. API (dev-режим)
uvicorn app.main:app --reload --port 8000

# 5. В отдельных терминалах:
faststream run workers.main:app                 # workers (outbox/inbox)
taskiq scheduler workers.sheduler:schedule      # планировщик очистки

# 6. Code Isolator (требуется доступный Docker daemon)
pip install -r code_sandbox/requirements.txt
cd code_sandbox
faststream run main:app
```

---

## 📡 API Reference

Автодокументация: **Swagger** `/docs`, **ReDoc** `/redoc`.
Все защищённые роуты принимают заголовок `Authorization: Bearer <access_token>`.

### 🔐 Авторизация — `/auth`

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/auth/` | — | Регистрация. Поля: `name`, `nik_name`, `email`, `password` (≥8 симв.), `password_confim`. Пароль хешируется Argon2. Возвращает `201` |
| `POST` | `/auth/login` | — | Логин (OAuth2 **form-data**: `username` = никнейм **или** email, `password`). Возвращает `{"access_token": "...", "token_type": "bearer"}` |
| `GET` | `/auth/me` | Bearer | Возвращает текущий токен |

**JWT payload:** `sub` (user id), `exp` (30 минут), `type` (`access`), `jti` (UUID).
Подпись — **RS256**; encode/decode выполняются в `asyncio.to_thread`.
При каждом запросе `jti` проверяется на наличие в Redis-blacklist (`black_list:{jti}`),
а `type` обязан быть `access`.

Пример регистрации:

```json
POST /auth/
{
  "name": "Ivan",
  "nik_name": "ivan_dev",
  "email": "ivan@example.com",
  "password": "supersecret1",
  "password_confim": "supersecret1"
}
```

### 🧩 Задачи — `/problems` (публичные)

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/problems/solution/{task_id}` | Детали задачи: `id`, `title`, `description`, `difficulty`, `starter_code`, `method_name`, `comments_count` (кэш 30с + lock) |
| `GET` | `/problems/task/{level}` | Список задач по сложности: `EASY` \| `MEDIUM` \| `HARD` (`id`, `title`, `difficulty`) |

### 📚 Категории — `/category` (публичные)

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/category/all` | Все категории `[{id, name}]` (кэш 60с) |
| `GET` | `/category/task/{cat_id}` | Категория + её задачи `{name, tasks: [{id, title, difficulty}]}` |

### 🧪 Решения — `/solution` (требуется Bearer)

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/solution/run/{task_id}` | Быстрый прогон: публикует job напрямую в RabbitMQ, возвращает `submission_id` (строка UUID). **Без записи в БД** |
| `POST` | `/solution/submit/{task_id}` | Официальная посылка: в одной TX создаёт `Submission (pending)` + `OutboxSub`. Ответ: `{id, status, created_at}` |
| `GET` | `/solution/result/{submission_id}` | Результат: Redis GET → Pub/Sub (ожидание 3с) → повторный GET → `{"status": "timeout"}` |

Body для run/submit:

```json
{ "code": "class Solution:\n    def two_sum_sorted(self, numbers, target):\n        ..." }
```

> ⚠️ **Обязательно** определи класс `Solution` с методом, совпадающим с `method_name` задачи —
> sandbox-харнесс инстанцирует `Solution()` и вызывает этот метод для каждого теста.

Формат результата (`ExecutionResult`):

```json
{
  "status": "accepted",
  "logs": ["..."],
  "output": "...",
  "exit_code": 0,
  "test_result": [
    { "passed": true, "actual": [0, 1] }
  ],
  "time_ms": 213.45
}
```

Статусы и как они определяются (`isolated/service.py`):

| Статус | Условие |
|---|---|
| 🟡 `pending` | Создан при submit, до получения результата |
| ⏱ `time_limit_exceeded` | `exit_code == 137` (контейнер убит по таймауту/OOM) |
| 💥 `runtime_error` | `exit_code != 0` или не удалось распарсить `test_result` |
| 🟢 `accepted` | Все тесты `passed == true` |
| 🔴 `wrong_answer` | Хотя бы один тест не пройден |

### 💬 Комментарии — `/coments` (требуется Bearer)

| Метод | Путь | Параметры | Описание |
|---|---|---|---|
| `GET` | `/coments/{task_id}` | — | **Свои** комментарии к задаче |
| `GET` | `/coments/user/all` | `limit=10`, `offset=0` | Все свои комментарии (новые сверху) |
| `GET` | `/coments/task/{task_id}` | `limit=10`, `offset=0` | Все комментарии задачи (с автором `{id, name}`) |
| `POST` | `/coments/task/{task_id}` | body `{comment}` | Создать → `201` |
| `PUT` | `/coments/task/{task_id}` | `comment_id` + body | Редактировать **свой** комментарий |
| `DELETE` | `/coments/task/{task_id}` | `comment_id` | Удалить **свой** комментарий → `200` |

Обновление/удаление защищены условием `WHERE id AND user_id AND task_id` —
чужой комментарий изменить нельзя.

### 🚨 Ошибки

Единый обработчик `AllExceptions` логирует traceback и возвращает JSON `detail`:

| Исключение | Код | Сообщение |
|---|---|---|
| `TaskNotFoundError` | 404 | Задача не найдена |
| `UserNotFound` | 401 | Пользователь не найден |
| `InvalidPasswordException` | 401 | Неправильно введён пароль |
| `CommentNotFound` | 404 | Вы ещё не оставили комментарии |
| `CategoryNotFound` | 404 | Категории не найдены |
| Rate limit | 429 | (при включённом middleware) |

---

## 🖥 Админ-панель

На базе **SQLAdmin** (`/admin`) подключены две модели:

- **Task** — полный CRUD: `title`, `description`, `difficulty`, `solution`,
  `starter_code`, `method_name`, `test_cases` (JSONB), `categories`
- **Category** — `name` + привязанные задачи

Сессия — cookie-based (`AuthenticationBackend`).

> ⚠️ Учётные данные админки захардкожены в `app/Admin/models.py`
> (`admin_` / `admin__`) — **только для разработки**. Перед любым публичным
> деплоем замени на секреты из окружения.

---

## 🐳 Code Sandbox

`code_sandbox/` — изолированный микросервис выполнения кода.
Он **ничего не знает про PostgreSQL** — только RabbitMQ, Redis и Docker Engine API.

### Конвейер обработки (`isolated/`)

```text
📥 subscribe.py     solution.execute (prefetch 40, NACK_ON_ERROR)
      │  msgspec-декод ExecutionRequest {mode, code, method_name, test_cases}
      ▼
🔧 harness.py       генерация скрипта: user code + class CodeRunner
      │             прогон test_cases: func(**case["input"]) == case["expected"]
      │             вывод: "###RESULT###" + JSON-массив результатов
      ▼
🐳 isolate.py       docker.containers.create → attach(stdin) → start
      │             код подаётся через stdin, ожидание wait_for(timeout=3с) → kill
      │             парсинг логов, извлечение JSON после маркера
      │             always: container.delete() в finally
      ▼
🧮 service.py       determine_status(exit_code, test_result) → SubmissionStatus
      ▼
📤 publish.py       asyncio.TaskGroup:
                    • mode == "submit" → RabbitMQ solution.result
                    • Redis SET result:submission:{id} (TTL 90с)
                    • Redis PUBLISH result:submission:{id}
```

### Ограничения контейнера (`ConfDcoker` в `shemas.py`)

| Параметр | Значение | Зачем |
|---|---|---|
| Image | `python:3.11-slim` | Минимальная поверхность атаки |
| Memory | **128 MB** | Защита от OOM-бомб |
| CPU | **0.5 core** (`NanoCpus=500_000_000`) | Защита от CPU-майнинга/бесконечных циклов |
| PIDs | **64** | Защита от fork-bomb |
| Network | **`none`** | Полный запрет сети |
| Root FS | **read-only** | Никакой записи на диск |
| `/tmp` | tmpfs `rw,noexec,nosuid,size=64m` | Единственная writable-точка, без exec |
| Capabilities | **`CapDrop: ALL`** | Без привилегий |
| SecurityOpt | `no-new-privileges:true` | Запрет повышения привилегий |
| User | `1000:1000` (non-root) | Запуск от непривилегированного UID |
| Timeout | 3с → `container.kill()` → exit 137 → `time_limit_exceeded` | Защита от зависаний |
| Concurrency | `asyncio.Semaphore(40)` | Ограничение числа одновременных контейнеров |

### Планы по production-изоляции

Docker здесь — воспроизводимый **development sandbox**. Архитектура намеренно
не привязана к технологии изоляции, поэтому execution backend планируется заменить на:

```text
🐳 Docker (dev)  ──►  🔥 Firecracker microVM  /  🛡️ gVisor (production)
```

---

## ⚙️ Workers

`beckend/workers/` — отдельный FastStream-процесс (`workers.main:app`),
в lifespan которого поднимаются две фоновые задачи: **Outbox Relay** и **Inbox Relay**.

### Настройки Outbox Relay

| Параметр | Значение |
|---|---|
| Батч из БД | 20 строк, `FOR UPDATE SKIP LOCKED`, сортировка по `created_at` |
| Конкурентность публикаций | `Semaphore(50)` |
| Таймаут одного publish | 10с |
| Ретраи | `MAX_RETRIES = 5`, затем `failed_at` |
| Backoff | `min(2^count, 60)` секунд от `last_attempt_at` |
| Пауза polling | 0.2с (батч полный) / 5с (БД пуста) |

### Настройки Inbox Relay

| Параметр | Значение |
|---|---|
| Prefetch канала | 50 |
| ACK-политика | `NACK_ON_ERROR` (requeue при сбое) |
| Внутренняя очередь | `asyncio.Queue(40)` |
| Батч | до 40 сообщений, ожидание следующего — 1с |
| Дедупликация | `SELECT` по `inboxsub.submission_id` → повторные сообщения просто ACK'аются |
| Запись | bulk `UPDATE submissions` + bulk `INSERT inboxsub` одной TX |
| Graceful shutdown | при `CancelledError` накопленный батч сохраняется в БД |

### Scheduler + Clear

- **taskiq** `StreamScheduler` с `LabelScheduleSource`: cron `0 */2 * * *`
  (каждые 2 часа) публикует сообщение `clear_db` в exchange `outbox_inbox` / queue `clear`.
- Воркер `clear_db.py` удаляет:
  - `inboxsub`, обработанные **> 24 часов** назад;
  - `outboxsub`, обработанные **> 24 часов** назад **или** помеченные как `failed_at`.

---

## 🔴 Redis в проекте

Redis используется в **пяти** ролях:

### 1. ⚡ Кэш чтения (`RedisCache`)

- Ключи: `task:{id}` (TTL **5ч**, для execution), `tasks:{level}` / `tasks:{id}`
  (TTL **30с**, каталог), `category:all` / `category:task:{id}` (TTL **60с**).
- **Jitter TTL** `±3с` — защита от массового одновременного истечения ключей.
- **Distributed lock** (`lock_key:...`, timeout 3с) — при cache miss в БД идёт
  только один запрос, остальные ждут и читают уже прогретый кэш:

```text
Request A ─┐
Request B ─┼─► miss ─► 🔒 Redis Lock ─► PostgreSQL ─► SET cache
Request C ─┘                                    ▲
              остальные читают из кэша ◄────────┘
```

- Массовая инвалидация: `SCAN` + `UNLINK` батчами по 500 ключей
  (`cache_del_prefix`, `cache_del_key`).

### 2. 🚦 Rate Limiting (`RateLimite`)

Sliding window на **sorted set** одним pipeline:
`ZREMRANGEBYSCORE` (срез окна) → `ZADD` (текущий запрос) → `ZCARD` (счётчик) → `EXPIRE`.
Лимит: **5 запросов / 5 секунд** на связку `IP + endpoint`; `/docs`, `/redoc`,
`/openapi.json` исключены. *Сейчас middleware отключён (закомментирован).*

### 3. 📡 Pub/Sub результатов

Канал = `result:submission:{id}`. Isolator делает `SET` (TTL 90с) + `PUBLISH`;
`GET /solution/result/{id}` подписывается и ждёт до 3с — клиент получает verdict
push'ем, без поллинга.

### 4. 🚫 Token Blacklist

`black_list:{jti}` со значением `1` и TTL = остаток жизни токена.
Проверяется в `current_token` при каждом защищённом запросе.

### 5. 🏆 Рейтинг (заготовка)

Класс `Raiting`: `ZINCRBY` + `ZREVRANGE` (top-N), месячный TTL по умолчанию.
Готов к подключению leaderboard-фич.

---

## 🐘 База данных

### Схема

```text
┌──────────┐       ┌──────────────┐        ┌────────────┐
│  users   │1─────*│  submissions │*─────1 │   tasks    │
│          │       │  id: UUID PK │        │            │
└────┬─────┘       └──────────────┘        └─────┬──┬───┘
     │1                                          │  │1
     │                                           │  │
     │*        ┌──────────────┐                  │  │*      ┌────────────┐
     └────────►│   comments   │*────────────────┘  └───────►│ type_tasks │
               └──────────────┘                             │  (m2m)     │
                                                            └─────┬──────┘
┌─────────────┐  outbox-паттерн    ┌──────────────┐               │1
│  outboxsub  │ (job на выполнение)│  inboxsub    │ (обработанные) ┌▼──────────┐
│ submission_id│                   │submission_id │               │ categories │
└─────────────┘                    └──────────────┘               └────────────┘
```

### Таблицы

| Таблица | Ключевые поля | Особенности |
|---|---|---|
| `users` | `id`, `name`, `nik_name` (unique), `email` (unique), `password`, `create_date`, `updated_at` | Пароль — Argon2-хеш |
| `tasks` | `id`, `title`, `description`, `difficulty` (PG ENUM), `solution` (JSONB), `starter_code`, `method_name`, `test_cases` (JSONB), `create_at`, `update_at` | Вычисляемое `comments_count` — коррелированный scalar subquery |
| `comments` | `id`, `user_id` FK⟶users, `task_id` FK⟶tasks, `comment`, `created_at`, `update_at` | `ON DELETE CASCADE`, индексы на FK |
| `submissions` | **`id` UUID PK**, `user_id`, `task_id`, `code`, `status` ENUM, `exit_code`, `output`, `time_ms`, `creadet_at` | Статусы: `pending / running / accepted / wrong_answer / runtime_error / time_limit_exceeded` |
| `categories` | `id`, `name` (unique) | — |
| `type_tasks` | `categories_id` + `task_id` (composite PK) | Many-to-many задачи↔категории |
| `outboxsub` | `submission_id` UUID PK, `message` (JSONB), `count`, `last_error`, `last_attempt_at` (timestamptz), `failed_at`, `created_at`, `processed_at` | Индексы: `failed_at`, `processed_at`, `last_attempt_at` |
| `inboxsub` | `submission_id` UUID PK, `payload` (JSONB), `processed_at` | Журнал обработанных результатов (идемпотентность) |

Подключение: SQLAlchemy 2.0 async + asyncpg, пул `pool_size=20, max_overflow=20,
pool_timeout=30, pool_pre_ping=True, pool_recycle=1800`. Доступ к БД в репозиториях
ограничен `asyncio.Semaphore(20)`.

### 🔄 История миграций (Alembic, async)

| # | Ревизия | Что делает |
|---|---|---|
| 1 | `30bd4bd8c30a` *clean* | Базовые таблицы: `users`, `tasks`, `comments`, `submissions` + индексы |
| 2 | `623f7ebae03b` | Таблицы `categories` и `type_tasks` (m2m) |
| 3 | `aa27ccefbc9f` | `tasks.difficulty`: VARCHAR → PostgreSQL ENUM `difficultylevel` |
| 4 | `8b162575e21e` | Таблицы `outboxsub` / `inboxsub`, unique на `categories.name` |
| 5 | `fb9ce9f01764` | `outboxsub.last_attempt_at` + индексы `failed_at`, `processed_at` |
| 6 | `cb35e609af29` | (эксперимент) индекс `users.password` |
| 7 | `a59869dd7996` | откат: удаление индекса `users.password` |
| 8 | `5239a45d9cb5` | `last_attempt_at` → `timestamptz` (timezone-aware) |
| 9 | `f4595e74f58a` | проверка (no-op) |

```bash
cd beckend
alembic upgrade head                                        # применить
alembic revision --autogenerate -m "message"                # создать миграцию
```

---

## 🧪 Тестирование

**pytest + pytest-asyncio + httpx** — тесты ходят в приложение напрямую через
`ASGITransport` (без поднятия сети), lifespan управляется `asgi-lifespan`.
Таблицы создаются через `Base.metadata.create_all` (`test_base()`).

| Файл | Покрытие |
|---|---|
| `conftest.py` | Фикстуры: `client` (чистый), `auth_client` (логин под `tesname`) |
| `test_auth.py` | Регистрация нового пользователя |
| `test_task.py` | `GET /problems/solution/1`, `GET /problems/task/MEDIUM` |
| `test_category.py` | `GET /category/all`, `GET /category/task/1` |
| `test_comm.py` | Полный цикл комментариев: create → get → all → by task → update → delete |
| `test_solution.py` | `POST /solution/run/1` и `/submit/1` (реальное решение Two Sum II) + `GET /solution/result/{id}` |

```bash
cd beckend
pytest test_/ -v
```

> 💡 Тесты ожидают: доступную БД из `.env`, созданные миграцией таблицы,
> задачу с `id=1` и пользователя `tesname` (создаётся `test_auth.py` —
> запускай файлы в алфавитном порядке или заранее создай данные).

---

## 📈 Нагрузочное тестирование

В `beckend/locustfile.py` — готовый Locust-сценарий:

```text
on_start: регистрация уникального бота (bot_<uuid>) → логин → Bearer-заголовок
@task:    POST /solution/submit/2  →  GET /solution/result/{submission_id}
wait_time: 1–2с между запросами
```

```bash
cd beckend
locust -f locustfile.py --host http://localhost:8001
# UI: http://localhost:8089
```

Сценарий нагружает весь критический путь: API → outbox → RabbitMQ → sandbox → inbox.

---

## 🗺 Roadmap

### ✅ Реализовано

- [x] Async FastAPI + Granian (production ASGI)
- [x] JWT RS256 (public/private keys) + Argon2
- [x] Token blacklist в Redis (механизм logout)
- [x] PostgreSQL + SQLAlchemy 2.0 async + asyncpg
- [x] Alembic async-миграции (9 ревизий)
- [X] rate-limit middleware
- [x] Redis: cache + locks + TTL jitter
- [x] Sliding-window rate limiter
- [x] RabbitMQ + FastStream (2 микросервиса)
- [x] **Transactional Outbox** с retry/backoff
- [x] **Inbox** с дедупликацией и батчевой записью
- [x] taskiq cron-scheduler + очистка таблиц
- [x] Docker sandbox с полным набором лимитов
- [x] Test runner (CodeRunner + JSON-маркер результата)
- [x] Redis Pub/Sub доставка результата клиенту
- [x] Категории задач (m2m)
- [x] Комментарии с пагинацией
- [x] SQLAdmin-панель
- [x] Полный Docker Compose (7 сервисов, healthchecks)
- [x] pytest-покрытие всех эндпоинтов
- [x] Locust-сценарий нагрузки
- [x] msgspec для брокерных сообщений

### 🚧 В работе / планах

**Execution**
- [ ] Ограничение размера пользовательского кода и stdout/stderr
- [ ] Стабилизация timeout/error handling
- [ ] Гарантированный cleanup контейнеров

**Security**
- [ ] 🔥 Firecracker / 🛡️ gVisor вместо Docker в production
- [ ] Refresh tokens + полноценный logout-эндпоинт (функция уже готова)
- [ ] Ролевая модель (`ReschePoints` dependency уже написан)
- [ ] Секреты админки в env вместо хардкода

**Messaging**
- [ ] Dead-letter queue для `failed_at` записей outbox
- [ ] Мониторинг зависших jobs

**Product**
- [ ] 🏆 Leaderboard (класс `Raiting` в Redis уже готов)
- [ ] 🔥 Streaks, achievements, статистика пользователя
- [ ] 🔎 Поиск, теги, скрытые тесты, кастомные валидаторы
- [ ] 👥 Contests
- [ ] 📈 Metrics + health checks, structured logging
- [ ] 🚀 CI/CD, мультиязычный sandbox

---

