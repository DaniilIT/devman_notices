import logging
from datetime import datetime
from pprint import pprint
from urllib.parse import urljoin

import requests
from requests.exceptions import ReadTimeout
from dotenv import dotenv_values

DEVMAN_URL = 'https://dvmn.org'
TIMEOUT = 120


# def fetch_reviews(token):
#     """" Получить список проверок
#     """
#     url = DEVMAN_URL + '/api/user_reviews/'
#     headers = {'Authorization': f'Token {token}'}
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#
#     reviews = response.json()
#     return reviews

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
    # reviews = fetch_reviews(devman_token)
    # pprint(reviews)

    timestamp = None

    for _ in range(3):
        try:
            response = fetch_reviews(devman_token, timestamp)
        except ReadTimeout as error:
            logging.error(f'Сервер не успел ответить.\n{error}\nУвеличьте время TIMEOUT.')
            break

        status = response.get('status')
        if status == 'timeout':
            timestamp = response.get('timestamp_to_request')
            logging.info(f'Работы еще на проверке.')
        elif status == 'found':
            timestamp = response.get('last_attempt_timestamp')
            # time_server = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')
            logging.info(f'Статус проверки работ изменился.')
            new_attempts = response.get('new_attempts')
            pprint(new_attempts)
        else:
            logging.error(f'Неожиданный ответ от сервера:\n{response}')


        # {'last_attempt_timestamp': 1681922270.298238,
        #  'new_attempts': [{'is_negative': False,
        #                    'lesson_title': 'Пишем сайт для риелторов',
        #                    'lesson_url': 'https://dvmn.org/modules/django-orm/lesson/filtering-products/',
        #                    'submitted_at': '2023-04-19T19:37:50.298238+03:00',
        #                    'timestamp': 1681922270.298238},
        #                   {'is_negative': True,
        #                    'lesson_title': 'Как гику сэкономить на спортивном '
        #                                    'снаряжении',
        #                    'lesson_url': 'https://dvmn.org/modules/mac-linux-command-line/lesson/coupon-scraper/',
        #                    'submitted_at': '2023-04-19T16:54:45.150151+03:00',
        #                    'timestamp': 1681912485.150151},
        #                   {'is_negative': True,
        #                    'lesson_title': 'Пишем сайт для риелторов',
        #                    'lesson_url': 'https://dvmn.org/modules/django-orm/lesson/filtering-products/',
        #                    'submitted_at': '2023-04-19T16:30:35.058517+03:00',
        #                    'timestamp': 1681911035.058517}],
        #  'request_query': [['timestamp', '1681825024.1560476']],
        #  'status': 'found'}


if __name__ == '__main__':
    logging.basicConfig(filename='responses.log', filemode='a', level=logging.INFO,
                        format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    main()
