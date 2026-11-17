# Course Service

## Архитектурное решение

Сервис построен по **гексагональной архитектуре (Ports and Adapters)**.
Бизнес-операции находятся в application-слое и зависят от портов, а не от
FastAPI, конкретного хранилища или Kafka.

```text
HTTP-адаптеры → application/use cases → порты
инфраструктурные адаптеры → порты
```

Ядро сервиса состоит из двух частей:

- `application` — use case, application services, порты и ошибки;
- `domain` — доменные сущности и чистые бизнес-правила. В текущей учебной
  версии отдельный `domain` пока не выделен, поскольку модели сервиса
  небольшие.

## Структура

```text
course_service/
├── application/
│   ├── container.py       # сборка приложения и DI
│   ├── errors.py          # ошибки application-слоя
│   └── ports.py           # контракты репозиториев, UoW и outbox
├── infrastructure/
│   ├── persistence/
│   │   ├── store.py       # in-memory состояние и snapshot
│   │   ├── outbox.py      # хранение outbox-сообщений
│   │   └── unit_of_work.py
│   └── messaging/
│       ├── dispatcher.py  # доставка outbox в publisher
│       └── mock_kafka.py  # учебный адаптер Kafka
├── repositories/          # текущие in-memory repository-адаптеры
├── services/              # application services
└── web/                   # FastAPI входной адаптер
```

`persistence` отвечает за сохранение состояния и транзакционные границы.
`messaging` отвечает за доставку сообщений во внешнюю систему. Поэтому
outbox-хранилище находится в `persistence`, а `OutboxDispatcher` и Kafka
publisher — в `messaging`.

## Unit of Work и outbox

При отправке решения операция выполняется так:

```text
Unit of Work begin
  ├── сохранить submission
  ├── добавить checks.command в transaction buffer
  └── добавить similarity.command в transaction buffer
commit
  └── сделать сообщения видимыми dispatcher
background task → MockKafkaPublisher
```

При ошибке выполняется rollback и submission вместе с командами не сохраняется.
Dispatcher читает только сообщения после commit.

`BackgroundTasks` используется как учебная имитация доставки после HTTP-ответа.
Это не отдельный надежный Kafka worker: при переходе к production его следует
заменить отдельным процессом или lifespan-worker с retry и контролируемым
завершением.

## Kafka-интеграция

Course Service не запускает код и не вычисляет плагиат. Внешние компоненты
представлены mock-адаптером и соответствуют схеме лабораторной:

```text
Course Service --checks.command----> Kafka ----> CodeCoordinator
Course Service --similarity.command-> Kafka ----> Plagiarism Service
CodeCoordinator --checks.events----> Kafka ----> Course Service
Plagiarism Service --similarity.events> Kafka -> Course Service
CodeCoordinator <---------------> Execution State Store
```

Используемые топики:

- `checks.command` — команда проверки решения;
- `checks.events` — прогресс и результат проверки;
- `similarity.command` — команда анализа сходства;
- `similarity.events` — прогресс и результат анализа.

`MockKafkaPublisher` только записывает опубликованные сообщения в память. Он
не поднимает настоящий Kafka и не запускает внешние сервисы.

## Использованные паттерны

- **Adapter** — FastAPI, in-memory repositories и `MockKafkaPublisher`
  адаптируют внешние технологии к портам application-слоя.
- **Facade** — application services скрывают последовательность бизнес-шагов.
- **Strategy** — тип review (`manual`/`auto`) определяет способ связывания
  результата с submission.
- **Unit of Work** — объединяет изменение состояния и запись outbox-команд.
- **Transactional Outbox** — сохраняет команды до их доставки во внешнюю
  систему.

## Проверки

Из каталога `course-service`:

```text
uv run pytest
uv run mypy src tests
uv run ruff check src tests
```
