# 🚀 Pyleet



## 🧠 О проекте

**Pyleet** — pet-project платформы для решения задач по программированию с автоматической проверкой пользовательского кода.

Основная идея проекта — построить backend, который умеет не только хранить задачи и пользователей, но и **асинхронно принимать пользовательский код, передавать его отдельному execution-сервису и возвращать результат проверки**.

Архитектура проекта состоит из двух основных компонентов:

```text
🌐 Main Application
        │
        │ RabbitMQ
        ▼
🧪 Code Isolator
        │
        ▼
🐳 Sandbox
```

Основное приложение отвечает за API, пользователей, задачи, submissions, комментарии, Redis и работу с PostgreSQL.

Отдельный **Code Isolator** отвечает исключительно за выполнение пользовательского кода.

Это позволяет не запускать потенциально опасный пользовательский код непосредственно внутри API-приложения.

---

# ⚡ Главная идея

Пользователь отправляет решение:

```text
👨‍💻 User
   │
   │ POST /TaskSolution/submit/{task_id}
   ▼
🌐 FastAPI
   │
   │ publish job
   ▼
📨 RabbitMQ
   │
   ▼
🧪 Code Isolator
   │
   ▼
🐳 Sandbox
   │
   ▼
🧪 Test Runner
   │
   ▼
📊 Result
   │
   ├──────────► 🐘 PostgreSQL
   │
   └──────────► 🔴 Redis
                    │
                    ▼
                 👨‍💻 User
```

Выполнение пользовательского кода не блокирует основной API.

---

# 🏗️ Архитектура

## 🌐 Main Application

Основное приложение построено на **FastAPI** и полностью работает в async/await модели.

Оно отвечает за:

- 🔐 authentication;
- 👤 users;
- 🧩 tasks;
- 📝 submissions;
- 💬 comments;
- 🗄️ database access;
- ⚡ Redis cache;
- 🚦 rate limiting;
- 📨 отправку execution jobs в RabbitMQ.

---

## 🧪 Code Isolator

Code Isolator — отдельное async-приложение на **FastStream**, которое слушает очередь RabbitMQ и выполняет пользовательские решения.

Его ответственность специально ограничена:

```text
📨 Receive execution job
        ↓
🧪 Build execution script
        ↓
🐳 Start sandbox
        ↓
▶️ Run user code
        ↓
🧪 Run tests
        ↓
📊 Build execution result
        ↓
🔴 Publish result
```

Основное приложение не знает деталей запуска контейнера.

Это позволяет в будущем менять сам механизм sandboxing, не перестраивая весь API.

---

# 🔄 Полностью асинхронный стек

Pyleet строится вокруг `asyncio`.

Основные компоненты работают асинхронно:

```text
⚡ FastAPI
⚡ SQLAlchemy Async
⚡ asyncpg
⚡ Redis asyncio client
⚡ FastStream
⚡ RabbitMQ
⚡ Docker API через aiodocker
```

Идея проекта — не создавать блокирующие операции в основном request/event loop.

Упрощённо:

```text
HTTP Request
     │
     ▼
 async FastAPI
     │
     ├── async PostgreSQL
     ├── async Redis
     └── async RabbitMQ
              │
              ▼
        async worker
              │
              ▼
        async Docker API
```

---

# 🧩 Возможности

## 🔐 Authentication

Сейчас реализованы:

- регистрация;
- login;
- JWT access token;
- Argon2 password hashing;
- OAuth2 Bearer authentication;
- проверка expiration;
- token validation.

Пароли не хранятся в открытом виде.

Для хеширования используется Argon2.

---

## 🧩 Tasks

Задача содержит:

```text
🆔 ID
📌 Title
📝 Description
🎯 Difficulty
💡 Starter Code
🔧 Method Name
🧪 Test Cases
📚 Solution
```

Тестовые данные хранятся в PostgreSQL в JSON/JSONB формате.

---

# 🧪 Code Execution

Это центральная часть проекта.

Пользовательский код **не выполняется внутри FastAPI application**.

Вместо этого создаётся execution job:

```text
FastAPI
   │
   ▼
RabbitMQ
   │
   ▼
Code Isolator
```

После получения job isolator создаёт sandbox и передаёт туда подготовленный Python script.

---

# 🐳 Development Sandbox

На текущем этапе для изоляции используется Docker.

Docker выбран прежде всего как **удобный и воспроизводимый development sandbox**, позволяющий уже сейчас разрабатывать и тестировать весь execution pipeline.

Контейнер запускается с ограничениями:

```text
🐍 Python 3.11

🧠 Memory limit
⚡ CPU limit
🧵 PID limit
🌐 Network disabled
📂 Read-only root filesystem
📁 Temporary writable /tmp
🛡️ Linux capabilities dropped
🔒 no-new-privileges
👤 Non-root user
```

То есть Docker здесь не просто используется как способ запустить Python — sandbox получает ограничения ресурсов и доступов.

---

# 🔥 Production Isolation

Docker **не является конечным production-решением** для запуска недоверенного пользовательского кода.

Его основная роль сейчас:

> 🧪 удобная среда разработки execution pipeline.

Для production планируется исследовать и использовать более специализированную изоляцию:

```text
🔥 Firecracker
        или
🛡️ gVisor
```

Цель:

- 🔐 более строгая изоляция;
- 🧠 контролируемое потребление ресурсов;
- ⏱️ предсказуемое выполнение;
- 🛡️ уменьшение attack surface;
- 📈 возможность дальнейшего масштабирования execution layer.

При этом архитектура приложения не должна зависеть от конкретной технологии sandbox.

Концепция:

```text
                Execution API
                     │
                     ▼
                Code Isolator
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      🐳 Docker          🔥 Firecracker
     development          / 🛡️ gVisor
                            production
```

---

# 📨 RabbitMQ

RabbitMQ используется для передачи execution jobs от Main Application к Code Isolator.

Основной queue:

```text
solution.execute
```

Например:

```json
{
  "mode": "submit",
  "code": "...",
  "method_name": "solve",
  "test_cases": []
}
```

API публикует сообщение и продолжает работу.

Worker получает сообщение независимо от API процесса.

---

# 🔴 Redis

Redis используется сразу в нескольких местах.

### ⚡ Cache

Задачи могут кэшироваться, чтобы не обращаться к PostgreSQL при каждом запросе.

Для защиты от одновременного cache miss используется Redis lock.

```text
Request A ─┐
Request B ─┼──► 🔒 Redis Lock ───► PostgreSQL
Request C ─┘
```

---

### 🚦 Rate Limiting

API использует Redis для ограничения частоты запросов.

Текущая конфигурация:

```text
5 requests / 5 seconds
```

---

### 📡 Pub/Sub

После выполнения решения Code Isolator публикует результат через Redis Pub/Sub.

```text
🧪 Isolator
      │
      ▼
🔴 Redis Pub/Sub
      │
      ▼
🌐 FastAPI
      │
      ▼
👨‍💻 Client
```

---

# 🐘 PostgreSQL

PostgreSQL является основным persistent storage.

Основные сущности:

```text
👤 Users
🧩 Tasks
💬 Comments
📝 Submissions
```

Используется:

- SQLAlchemy 2.0;
- asyncpg;
- Alembic.

Все database операции построены вокруг async SQLAlchemy.

---

# 📝 Submissions

При `submit` решение сохраняется в PostgreSQL.

Submission содержит:

```text
🆔 ID
👤 User
🧩 Task
💻 Source Code
📊 Status
💥 Exit Code
📤 Output
⏱️ Execution Time
```

Поддерживаются следующие состояния:

```text
🟡 pending
🔵 running
🟢 accepted
🔴 wrong_answer
💥 runtime_error
⏱️ time_limit_exceeded
```

---

# 🧪 Test Runner

Для каждой задачи задаются test cases.

Упрощённый процесс:

```text
User Code
    +
Test Cases
    ↓
CodeRunner
    ↓
Function Execution
    ↓
Expected vs Actual
    ↓
Execution Result
```

Runner собирает результаты выполнения отдельных тестов и передаёт их обратно в систему.

---

# 💬 Comments

Пользователи могут работать с комментариями задач.

Поддерживаются:

- ➕ создание;
- 📖 получение;
- ✏️ редактирование;
- 🗑️ удаление;
- 📄 pagination;
- 🔎 получение комментариев конкретной задачи.

---

# 📡 API

## 🔐 Authentication

```http
POST /auth/
POST /auth/login
GET  /auth/me
```

## 🧪 Solutions

```http
GET  /TaskSolution/task/solution/{task_id}

POST /TaskSolution/run/{task_id}
GET  /TaskSolution/run/result/{submission_id}

POST /TaskSolution/submit/{task_id}
GET  /TaskSolution/submit/result/{submission_id}
```

## 💬 Comments

```http
GET    /coments/{task_id}
GET    /coments/all
GET    /coments/task/{task_id}

POST   /coments/task/{task_id}

PUT    /coments/task/{task_id}
DELETE /coments/task/{task_id}
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 📁 Структура проекта

```text
pyleet/
│
├── beckend/
│   │
│   ├── app/                         🌐 Main Application
│   │   │
│   │   ├── auth/                    🔐 Authentication
│   │   │   ├── auth.py
│   │   │   └── login.py
│   │   │
│   │   ├── brokers/                 📨 RabbitMQ
│   │   │   ├── connection.py
│   │   │   └── publish.py
│   │   │
│   │   ├── database/                🐘 PostgreSQL
│   │   │   ├── db.py
│   │   │   ├── models/
│   │   │   └── shemas/
│   │   │
│   │   ├── redis_client/            🔴 Redis
│   │   │   ├── redis_cache.py
│   │   │   ├── redis_connect.py
│   │   │   ├── redis_limite.py
│   │   │   └── redis_raiting.py
│   │   │
│   │   ├── routers/                 🚏 API
│   │   │   ├── coments_user.py
│   │   │   ├── repositories.py
│   │   │   ├── service.py
│   │   │   └── solution_router.py
│   │   │
│   │   ├── dependcies.py
│   │   ├── exceptions.py
│   │   └── main.py
│   │
│   ├── code_sandbox/                🧪 Code Isolator
│   │   ├── harness.py
│   │   ├── isolate.py
│   │   ├── main.py
│   │   └── shemas.py
│   │
│   ├── alembic/                     🔄 Migrations
│   │   └── versions/
│   │
│   ├── config.py
│   ├── alembic.ini
│   └── requirements.txt
│
├── compose.yaml                     🐳 Infrastructure
└── .gitignore
```

---

# 🚀 Запуск

## 1. Clone

```bash
git clone https://github.com/j35203380-pn/pyleet.git
cd pyleet
```

## 2. Virtual environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

## 3. Dependencies

```bash
pip install -r beckend/requirements.txt
```

---

# 🐘 Infrastructure

Для локальной разработки используются:

```text
🐘 PostgreSQL
🔴 Redis
🐇 RabbitMQ
🐳 Docker
```

PostgreSQL уже описан в `compose.yaml`.

Запуск:

```bash
docker compose up -d
```

Redis и RabbitMQ должны быть доступны для приложения отдельно на текущем этапе.

---

# ⚙️ Environment

Создай:

```text
beckend/.env
```

Пример:

```env
POSTGRES_HOST=localhost
POSTGRES_USER=pyleet
POSTGRES_PASSWORD=secret
POSTGRES_NAME=pyleet
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_USER=
REDIS_PORT=6379
REDIS_PASSWORD=

RBROKER_HOST=localhost
RBROKER_USER=guest
RBROKER_PORT=5672
RBROKER_PASSWORD=guest

JWT_SECRET_KEY=keys/private.pem
JWT_PUBLIC_KEY=keys/public.pem
ALGORITHM=RS256
```

🔐 `.env` и private keys не должны попадать в Git.

---

# 🗄️ Migrations

```bash
cd beckend
alembic upgrade head
```

Создание новой миграции:

```bash
alembic revision --autogenerate -m "your message"
```

---

# 🌐 Start Main Application

```bash
cd beckend
uvicorn app.main:app --reload
```

После запуска:

```text
🌐 API       → http://localhost:8000
📚 Swagger   → http://localhost:8000/docs
📖 ReDoc     → http://localhost:8000/redoc
```

---

# 🧪 Start Code Isolator

Code Isolator находится в:

```text
beckend/code_sandbox/
```

Он подключается к RabbitMQ и ожидает execution jobs.

В дальнейшем планируется запускать Main Application и Code Isolator как отдельные containers через Docker Compose.

---

# 🗺️ Roadmap

## ✅ Implemented

- [x] 🚀 Async FastAPI backend
- [x] 🔐 JWT authentication
- [x] 🔑 Argon2 password hashing
- [x] 🐘 PostgreSQL
- [x] ⚡ SQLAlchemy Async
- [x] 🔄 Alembic migrations
- [x] 🔴 Redis
- [x] 🧠 Redis cache
- [x] 🔒 Redis locks
- [x] 🚦 Rate limiting
- [x] 📨 RabbitMQ
- [x] 🐇 Async Code Isolator
- [x] 🐳 Docker development sandbox
- [x] 🧪 Test runner
- [x] 📝 Submissions
- [x] 💬 Comments

---

## 🚧 In Progress

### 🧪 Execution

- [ ] исправить и стабилизировать execution pipeline
- [ ] унифицировать execution schemas
- [ ] улучшить обработку результатов тестов
- [ ] улучшить timeout handling
- [ ] улучшить runtime error handling
- [ ] ограничить stdout/stderr
- [ ] гарантировать cleanup sandbox

### 🔐 Security

- [ ] усилить sandbox isolation
- [ ] ограничить размер пользовательского кода
- [ ] ограничить размер output
- [ ] дополнительные resource limits
- [ ] улучшить token management

### 📨 Messaging

- [ ] retry failed jobs
- [ ] dead-letter queue
- [ ] job recovery
- [ ] обработка зависших jobs

---

# 🔥 Next Big Step — Production Sandbox

Главное архитектурное направление проекта:

```text
🐳 Docker
     │
     │ development
     ▼
Execution Pipeline
     │
     ▼
🔥 Firecracker
        /
🛡️ gVisor
     │
     ▼
Production Code Execution
```

Цель — сохранить существующий execution pipeline, заменив development sandbox на более специализированный production isolation layer.

---

# 📊 В будущем

Планируются:

- [ ] 🔄 Refresh tokens
- [ ] 🏆 User statistics
- [ ] 🔥 Streak system
- [ ] 🥇 Achievements
- [ ] 🏅 Leaderboard
- [ ] 📚 Problem categories
- [ ] 🏷️ Tags
- [ ] 🔎 Search
- [ ] 🔒 Hidden test cases
- [ ] 🧪 Custom validators
- [ ] 👥 Contests
- [ ] 📈 Metrics
- [ ] ❤️ Health checks
- [ ] 📜 Structured logging
- [ ] 🧪 Unit tests
- [ ] 🔬 Integration tests
- [ ] 🔗 End-to-End tests
- [ ] 🐳 Full Docker Compose environment
- [ ] 🚀 CI/CD

---

# 🧠 Почему этот проект интересен

Pyleet создаётся не просто как CRUD API.

В проекте постепенно собирается целая цепочка:

```text
🌐 HTTP
   ↓
⚡ Async Python
   ↓
📨 Message Broker
   ↓
🧪 Async Worker
   ↓
🐳 Sandbox
   ↓
🧪 Code Execution
   ↓
📊 Result Processing
   ↓
🔴 Redis
   ↓
🐘 PostgreSQL
```

Самая интересная часть проекта — **безопасное выполнение пользовательского кода в отдельном execution layer**.

Docker сейчас используется как удобная development-среда, а архитектура заранее строится так, чтобы в будущем execution backend можно было заменить на Firecracker или gVisor.

---

# 🚧 Project Status

**Pyleet находится в активной разработке.**

Проект ещё не является production-ready системой.

Основной текущий фокус:

```text
🧪 Stable Execution
        ↓
🔐 Strong Isolation
        ↓
📨 Reliable Messaging
        ↓
🧪 Testing
        ↓
📊 Observability
        ↓
🚀 Production
```

