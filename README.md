# Telegram-бот для приёма заявок на IT-услуги

Bot (aiogram) + Mini App форма (FastAPI + статика) + SQLite.

## Структура

```
telegram-order-bot/
  app/
    config.py        # переменные окружения
    db.py             # SQLite: сохранение и чтение заявок
    telegram_auth.py  # проверка подписи initData от Mini App
    handlers.py       # /start и меню бота
    bot.py            # запуск бота (polling)
    webapp.py         # FastAPI: отдаёт форму + принимает заявки
  static/
    index.html        # форма Mini App
    style.css
    app.js
```

## 1. Установка

```bash
cd telegram-order-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполни `.env`:
- `BOT_TOKEN` — получить у @BotFather (`/newbot`)
- `WEBAPP_URL` — публичный HTTPS-адрес, где будет висеть форма (см. ниже)
- `ADMIN_CHAT_ID` — твой chat_id для уведомлений (узнать через @userinfobot)

## 2. Локальный запуск (для теста)

Два отдельных процесса:

```bash
# терминал 1 — сам бот
python -m app.bot

# терминал 2 — веб-форма
uvicorn app.webapp:app --host 0.0.0.0 --port 8001
```

Telegram Mini App **обязательно требует HTTPS**, localhost не подойдёт — для локальных тестов
можно временно пробросить порт через `ngrok http 8001` и подставить выданный ngrok-адрес в
`WEBAPP_URL` и в настройки бота у @BotFather.

## 3. Прод-деплой на твоём VPS (там же, где ypklementev.ru)

**Поддомен**: например `order.ypklementev.ru`, тот же сертификат Let's Encrypt (certbot добавит
его в SAN автоматически или отдельным `certbot --nginx -d order.ypklementev.ru`).

**Nginx** (проксирует на uvicorn на 8001):

```nginx
server {
    server_name order.ypklementev.ru;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    # ssl_certificate / ssl_certificate_key добавит certbot
}
```

**systemd**, два юнита в `/etc/systemd/system/`:

`order-bot.service`:
```ini
[Unit]
Description=Telegram order bot (polling)
After=network.target

[Service]
WorkingDirectory=/path/to/telegram-order-bot
ExecStart=/path/to/telegram-order-bot/venv/bin/python -m app.bot
Restart=always
EnvironmentFile=/path/to/telegram-order-bot/.env

[Install]
WantedBy=multi-user.target
```

`order-webapp.service`:
```ini
[Unit]
Description=Telegram order webapp (FastAPI)
After=network.target

[Service]
WorkingDirectory=/path/to/telegram-order-bot
ExecStart=/path/to/telegram-order-bot/venv/bin/uvicorn app.webapp:app --host 127.0.0.1 --port 8001
Restart=always
EnvironmentFile=/path/to/telegram-order-bot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now order-bot order-webapp
```

## 4. Настройка Mini App у @BotFather

`/mybots` → выбрать бота → `Bot Settings` → `Menu Button` → указать URL `WEBAPP_URL`
(это добавит кнопку с формой прямо в интерфейс чата, в дополнение к inline-кнопке,
которая уже зашита в `/start`).

## Что дальше (не входит в этот билд, но логично добавить)

- Простая админ-панель (список заявок, смена статуса) — `db.py` уже готов к этому
- Кнопки "Взять в работу" / статус прямо под уведомлением в боте
- Rate-limit на `/api/order`, чтобы не заспамили форму
