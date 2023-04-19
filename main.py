from pprint import pprint

import requests
from dotenv import dotenv_values

DEVMAN_URL = 'https://dvmn.org/api'


def fetch_reviews(token):
    """" Получить список проверок
    """
    url = DEVMAN_URL + '/user_reviews/'
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    reviews = response.json()
    return reviews


def main():
    devman_token = dotenv_values('.env')['DEVMAN_TOKEN']
    reviews = fetch_reviews(devman_token)
    pprint(reviews)


if __name__ == '__main__':
    main()
