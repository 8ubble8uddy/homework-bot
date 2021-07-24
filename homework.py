import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
)

logger = logging.getLogger(__name__)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def restart_after(seconds):
    m = int(seconds / 60)
    s = seconds - m * 60
    logger.debug(f'Повторный запрос через {m} мин. и {s} сек.')
    time.sleep(seconds)


def main():
    current_timestamp = int(time.time())
    i = 0

    while True:
        try:
            logger.debug('Отправляется запрос к API сервису Практикум.Домашка')
            homeworks = get_homeworks(current_timestamp)
            logger.info(f'Получен ответ: {homeworks}')
            if homeworks['homeworks']:
                logger.debug('Работа проверена!')
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                logger.debug(f'Отправляется сообщение: {message}.')
                result = send_message(message)
                logger.info(f'Сообщение было отправлено: {result}.')
                break
            logger.debug('Работа не проверена.')
            restart_after(10)

        except Exception as e:
            message = f'Бот упал с ошибкой: {e}.'
            logger.exception(message)
            i += 1
            if i > 1:
                restart_after(60)
                continue
            try:
                logger.debug(f'Отправляется сообщение: {message}.')
                result = send_message(message)
                logger.info(f'Сообщение было отправлено: {result}.')
                restart_after(60)
            except Exception:
                i = 0
                message = f'Не удалось отправить уведомление об ошибке {e}.'
                logger.exception(message)
                restart_after(60)


if __name__ == '__main__':
    main()
