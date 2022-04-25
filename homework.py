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
ROOT_API_URL = 'https://practicum.yandex.ru'

bot = telegram.Bot(token=TELEGRAM_TOKEN)


class InvalidApiKeyError(Exception):
    pass


class InvalidApiValueError(Exception):
    pass


class FailedApiRequestError(Exception):
    pass


def parse_homework_status(homework):
    logger.debug('Проверка значений homework на соответствие ожиданиям.')
    try:
        homework_name = homework['homework_name']
        status = homework['status']
        homework_statuses = ['reviewing', 'rejected', 'approved']
        assert status in homework_statuses
    except KeyError as key:
        msg = f'Ключ {key} отсутствует в массиве значений по ключу "homeworks"'
        raise InvalidApiKeyError(msg)
    except AssertionError:
        msg = f'{homework_name} получил неизвестный статус - {status}'
        raise InvalidApiValueError(msg)
    else:
        logger.debug('Работа поступила на рассмотрение.')
        if status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        elif status == 'approved':
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        else:
            return f'У вас взяли работу "{homework_name}" на проверку.'
        logger.debug('Работа проверена!')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def check_homework(response):
    logger.debug('Проверка значений response на соответствие ожиданиям.')
    try:
        homework = response['homeworks']
    except KeyError as key:
        msg = f'Ключ {key} отсутствует в объекте полученных данных response'
        raise InvalidApiKeyError(msg)
    else:
        logger.info(f'Получен массив значений по ключу "homeworks" {homework}')
        return homework[0]


def get_homeworks(current_timestamp):
    logger.debug('Отправляется запрос к API сервису Практикум.Домашка.')
    url = f'{ROOT_API_URL}/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        response = homework_statuses.json()
    except Exception as request:
        msg = f'При GET-запросе ресурса {url} произошла ошибка {request}'
        raise FailedApiRequestError(msg)
    else:
        logger.info(f'Получен ответ: {response}')
        return response


def send_message(message):
    while True:
        try:
            logger.debug(f'Отправка сообщения: {message}')
            result = bot.send_message(chat_id=CHAT_ID, text=message)
        except telegram.error.TelegramError as tg:
            msg = f'При отправке сообщения {message} произошла ошибка {tg}.'
            logger.exception(msg)
            restart_after(5 * 60)
        else:
            logger.info(f'Сообщение было отправлено: {result}')
            return result


def restart_after(seconds):
    m = int(seconds / 60)
    s = seconds - m * 60
    logger.debug(f'Повторный запрос через {m} мин. и {s} сек.')
    time.sleep(seconds)


def main():
    current_timestamp = int(time.time())
    is_sent_message = False

    while True:
        try:
            response = get_homeworks(current_timestamp)
            homework = check_homework(response)
            message = parse_homework_status(homework)
            send_message(message)

        except IndexError:
            message = 'Работа не проверена.'
            logger.debug(message)

        except Exception as e:
            message = f'Бот упал с ошибкой: {e}.'
            logger.exception(message)
            if not is_sent_message:
                send_message(message)
            is_sent_message = True

        else:
            is_sent_message = False
            current_timestamp = int(time.time())

        finally:
            restart_after(20 * 60)


if __name__ == '__main__':
    main()
