import logging
# from datetime import datetime
from time import sleep
from urllib.parse import urljoin

import requests
import telegram
from dotenv import dotenv_values
from requests.exceptions import ReadTimeout

DEVMAN_URL = 'https://dvmn.org'
TIMEOUT = 120


def fetch_reviews(token, timestamp=None):
    """" Получить список проверок через long polling
    """
    url = urljoin(DEVMAN_URL, '/api/long_polling/')
    headers = {'Authorization': f'Token {token}'}
    payload = {'timestamp': timestamp} if timestamp else {}
    response = requests.get(url, headers=headers, params=payload, timeout=TIMEOUT)
    response.raise_for_status()

    return response.json()


def main():
    devman_token = dotenv_values('.env')['DEVMAN_TOKEN']
    telegram_token = dotenv_values('.env')['TELEGRAM_TOKEN']
    chat_id = dotenv_values('.env')['CHAT_ID']

    bot = telegram.Bot(token=telegram_token)
    timestamp = 1681922260  # None
    while True:
        try:
            response = fetch_reviews(devman_token, timestamp)
        except ReadTimeout:
            logging.warning(f'Сервер не успел ответить. Увеличьте время TIMEOUT.')
        except requests.ConnectionError:
            logging.warning(f'Интернет отключился. Переподключение...')
            sleep(1)
        else:
            status = response.get('status')
            if status == 'timeout':
                timestamp = response['timestamp_to_request']
                logging.info('Работы еще ожидают ревью.')
            elif status == 'found':
                timestamp = response['last_attempt_timestamp']
                # time_server = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')
                logging.info('Статус проверки работ изменился.')
                for attempt in response['new_attempts']:
                    review = 'К сожалению, в работе нашлись ошибки\.' if attempt['is_negative'] \
                        else 'Преподавателю всё понравилось, можно приступать к следующему уроку\!'
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"У Вас проверили работу [\"{attempt['lesson_title']}\"]({attempt['lesson_url']})\."
                             f"\n\n{review}",
                        parse_mode=telegram.ParseMode.MARKDOWN_V2
                    )
            else:
                logging.error(f'Неожиданный ответ от сервера:\n{response}')


if __name__ == '__main__':
    logging.basicConfig(filename='responses.log', filemode='a', level=logging.INFO,
                        format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    main()
    # str = f'{BAD_ATTEMPT if True else GOOD_ATTEMPT}'
    # print(str)
