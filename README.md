# ЭЛОУ-АВТ Digital Twin — Integrated MVP

## Состав
- `elou_avt_twin/` — Python Digital Twin + FastAPI REST/WebSocket backend.
- `elou_avt_web/` — React HMI (Vite + React Flow): технологическая схема, телеметрия, управление.
- `START_ALL.bat` — запуск backend и web-фронтенда.
- `elou_avt_twin/run_backend.bat` — запуск backend отдельно.

## Быстрый запуск
Требуется Windows 10/11, Python 3.11+ и Node.js 18+ (npm).

### Установка с нуля (после клонирования)
```bat
REM 1. Установка Python-зависимостей бэкенда
cd elou_avt_twin
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

REM 2. Установка зависимостей фронтенда
cd elou_avt_web
npm ci
cd ..

REM 3. Запуск обоих сервисов
START_ALL.bat
```

Либо просто запусти `START_ALL.bat` — он сам создаст venv, поставит зависимости
и запустит backend + web. Обрати внимание: `node_modules/`, `.venv/` и `dist/`
не хранятся в git, поэтому после клонирования **обязательно** выполнить
`pip install -r requirements.txt` и `npm install` (это делает `START_ALL.bat`).

### Запуск
1. Запусти `START_ALL.bat`.
2. Backend будет доступен на `http://127.0.0.1:8000/docs`.
3. Web-интерфейс откроется на `http://localhost:5173`.
4. Для демонстрации аварии используй инжекцию отказа через UI или `POST /failure/{equipment_id}`.

### Демо-вход

На экране входа сохранены кнопки быстрого входа. Пароль каждой демонстрационной
учётной записи совпадает с логином:

- `admin` — администратор;
- `instructor` — инструктор;
- `operator` — консольный оператор;
- `field_operator` — полевой оператор с 3D-экраном.

Это намеренное поведение MVP для показа КТК. Перед размещением вне закрытого
демо-контура смените пароли и задайте переменные окружения из раздела ниже.

## API
- `GET /health`
- `GET /state`
- `GET /alarms`
- `GET /events`
- `GET /score`
- `POST /input`
- `POST /action`
- `POST /scenario/start`
- `POST /scenario/reset`
- `POST /scenario/step`
- `POST /failure/{equipment_id}`
- `WS /ws/simulation`

## Демонстрационный сценарий
1. Запустить систему.
2. Показать технологическую схему (React Flow).
3. Инжектировать отказ насоса.
4. Показать изменение состояния и тревоги.
5. Запустить резервный насос через API/UI-интеграцию.
6. Показать восстановление процесса.

## Конфигурация безопасности

- `ELOU_AUTH_MODE=enabled` — режим по умолчанию; API требует Bearer-токен.
- `ELOU_AUTH_SECRET` — секрет подписи токенов длиной не менее 32 символов.
  В локальном режиме он создаётся автоматически в `.auth_secret`; в
  `ELOU_ENV=production` переменная обязательна.
- `ELOU_CORS_ORIGINS` — список разрешённых origins через запятую. По умолчанию
  разрешены только локальные Vite dev/preview адреса.
- `ELOU_AUTH_MODE=disabled` допустим только для локальной диагностики и запрещён
  при `ELOU_ENV=production`.

Токен WebSocket передаётся через subprotocol, а не в URL. Вход ограничен по
числу неудачных попыток. Схемы загружаются только из каталога `schemes/`.

## Схемы и дубли ID

Схемы автоматически мигрируются к формату `1.2`. Все узлы и связи сохраняются:
первый объект оставляет исходный ID, последующие получают детерминированный
суффикс `__dupN`. Неоднозначные старые связи остаются у первого объекта —
автоматического угадывания и скрытой перепривязки нет.

Повторная безопасная нормализация всех файлов:

```bash
cd elou_avt_twin
python tools/normalize_scheme_ids.py
```

## Проверка

```bash
cd elou_avt_twin
python -m pytest -q
python demo.py

cd ../elou_avt_web
npm ci
npm run build
node tools/benchmark_3d_model.mjs public/avt4_3d_model_v7.html
```

Подробности изменений и точки роста физического ядра приведены в
`REFACTORING_REPORT.md`.

## Важно
Физическое ядро является MVP-моделью. Для промышленного применения необходима дальнейшая валидация термодинамики и MESH-решателя.
