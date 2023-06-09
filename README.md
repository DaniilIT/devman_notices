# DEVMAN notices

Это серверная часть бота в telegram, который автоматически с помощью Long polling запросов
присылает уведомления о проверке работ на [DEVMAN](https://dvmn.org/).


## Как установить

Установите зависимости командой: 

```sh
pip install -r requirements.txt
```

Часть настроек проекта берётся из переменных окружения:

* `DEVMAN_TOKEN` - Чтобы идентифицировать DEVMAN аккаунт, вам потребуется токен доступа, получите его [здесь](https://dvmn.org/api/docs/).
* `TELEGRAM_TOKEN` - Чтобы использовать BotFather (telegram бот), вам потребуется токен доступа, получите его [здесь](https://telegram.me/BotFather).
* `TG_CHAT_ID` - Чтобы назначить telegram чат, вам потребуется chat id, получите его [здесь](https://telegram.me/userinfobot).

Вставьте токены и chat id, в файл .env, в формате `ПЕРЕМЕННАЯ=значение`.
TG_CHAT_ID вы можете не указывать здесь, если укажите её при запуске в качестве аргумента.


## Запуск

Для запуска бота наберите команду:

```sh
python main.py --tg_chat_id <your_tg_chat_id>
```

Если вы не указали TG_CHAT_ID в файле .env, то укажите здесь в качестве аргумента.


## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
