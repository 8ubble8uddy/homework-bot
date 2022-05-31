# HomeworkBot

[![CI](https://github.com/8ubble8uddy/homework-bot/workflows/homework-bot/badge.svg
)](https://github.com/8ubble8uddy/homework-bot/actions/workflows/hwbot_workflow.yml)

<kbd><img width="400" src="https://user-images.githubusercontent.com/83628490/171296374-c3766223-8aa7-4981-8040-f9d20a58ca50.png"></kbd>
<kbd><img width="400" src="https://user-images.githubusercontent.com/83628490/171296412-7e51528d-663b-4902-95b3-4f2f55728f8a.png"></kbd>

### **Описание**

_[homework-bot](https://github.com/8ubble8uddy/homework-bot) - это Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнаёт статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку._

### **Технологии**

```Python``` ```python-telegram-bot``` ```pytest``` ```Docker```

### **Как запустить проект:**

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/8ubble8uddy/homework-bot.git
```
```sh
cd homework-bot
```

Создать файл .env и добавить настройки для включения бота-ассистента:
```sh
nano .env
```
```
PRAKTIKUM_TOKEN = <ваш токен для доступа к API Практикум.Домашка>
TELEGRAM_TOKEN = <токен бота для работы с Bot API Telegram>
TELEGRAM_CHAT_ID = <ID вашего Telegram-аккаунта>
```

Скачать образ и запустить контейнер с проектом:
```
docker run -d --env-file .env 8ubble8uddy/homework_bot:latest
```

### Автор: Герман Сизов
