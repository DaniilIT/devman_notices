import argparse
import logging
from time import sleep
from urllib.parse import urljoin

import requests
import telegram
from dotenv import dotenv_values

DEVMAN_URL = 'https://dvmn.org'
TIMEOUT = 120


def create_parser():
    """ Функция производит синтаксический анализ командной строки.
    """
    parser = argparse.ArgumentParser(
        description='Программа присылает уведомления о проверке работ курсов DEVMAN.'
    )
    parser.add_argument(
        '--chat_id',
        help='Идентификатор чата telegram',
        default=dotenv_values('.env').get('CHAT_ID'),
    )
    return parser


def fetch_reviews(token, timestamp=None):
    """" Получить список проверок через long polling
    """
    url = urljoin(DEVMAN_URL, '/api/long_polling/')
    headers = {'Authorization': f'Token {token}'}
    payload = {'timestamp': timestamp} if timestamp else {}
    reviews = requests.get(url, headers=headers, params=payload, timeout=TIMEOUT)
    reviews.raise_for_status()

    return reviews.json()


def main():
    logging.basicConfig(filename='responses.log', filemode='a', level=logging.INFO,
                        format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

    args = create_parser().parse_args()
    chat_id = args.chat_id
    devman_token = dotenv_values('.env')['DEVMAN_TOKEN']
    telegram_token = dotenv_values('.env')['TELEGRAM_TOKEN']

    bot = telegram.Bot(token=telegram_token)
    timestamp = None
    while True:
        try:
            reviews = fetch_reviews(devman_token, timestamp)
        except requests.exceptions.ReadTimeout:
            logging.warning(f'Сервер не успел ответить. Увеличьте время TIMEOUT.')
        except requests.ConnectionError:
            logging.warning(f'Интернет отключился. Переподключение...')
            sleep(1)
        else:
            status = reviews.get('status')
            if status == 'timeout':
                timestamp = reviews['timestamp_to_request']
                logging.info('Работы еще ожидают ревью.')
            elif status == 'found':
                timestamp = reviews['last_attempt_timestamp']
                logging.info('Статус проверки работ изменился.')
                for attempt in reviews['new_attempts']:
                    review = 'К сожалению, в работе нашлись ошибки\.' if attempt['is_negative'] \
                        else 'Преподавателю всё понравилось, можно приступать к следующему уроку\!'
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"У Вас проверили работу [\"{attempt['lesson_title']}\"]({attempt['lesson_url']})\."
                             f"\n\n{review}",
                        parse_mode=telegram.ParseMode.MARKDOWN_V2
                    )
            else:
                logging.error(f'Неожиданный ответ от сервера:\n{reviews}')


if __name__ == '__main__':
    main()
