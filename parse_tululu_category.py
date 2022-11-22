from pprint import pprint

import requests
from main import WrongUrl, check_for_redirect, parse_book_page, sanitize_filename, download_txt, download_image
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import argparse
import re
import time
import json


def create_parser():
    parser = argparse.ArgumentParser(description='Bot for load images to Telegram channel')
    parser.add_argument('--category', nargs='?', default='l55',
                        help='Categories of books. Default "l55".')
    parser.add_argument('--start_page', type=int, nargs='?', default=1,
                        help='Start page for download. Default 1.')
    parser.add_argument('--end_page', type=int, nargs='?', default=702,
                        help='End page for download, not included. Default 702.')
    return parser


def main():
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    books_category = command_line_arguments.category
    load_dotenv()
    books_directory = os.environ['BOOKS_DIRECTORY']
    images_directory = os.environ['IMAGES_DIRECTORY']
    site_url = os.environ['SITE_URL']
    timeout = 10
    start_page = command_line_arguments.start_page
    end_page = command_line_arguments.end_page
    pattern = re.compile(r'\d+')
    team_books=[]


    for page in range(start_page, end_page):
        response = requests.get(urljoin(site_url, f"{books_category}/{page}/"))
        response.raise_for_status()
        soup_result = BeautifulSoup(response.text, "html.parser")

        selector = "div#content table.d_book a"
        a_tags = soup_result.select(selector)

        url = ''
        for tag in a_tags:
            if tag.text == 'скачать книгу' or tag.text == 'читатели о книге':
                url = urljoin(site_url, tag.get('href'))
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    check_for_redirect(response)
                    url_components = urlparse(url)
                    book_id = pattern.findall(url_components.path)[0]
                    book = parse_book_page(response, book_id)
                    payload = {"id": book_id}
                    file_name = sanitize_filename(book['title'])
                    download_txt(f'{file_name}.txt', book['url'], payload, books_directory)
                    download_image(book['img'], None, images_directory)
                    team_books.append(book)
                except requests.exceptions.TooManyRedirects:
                    print(f'TooManyRedirects. ИД = {book_id}, ошибочное перенаправление.')
                except WrongUrl:
                    print(f'WrongUrl. ИД = {book_id}, нет ссылки для скачивания.')
                except requests.exceptions.ConnectionError:
                    print(f'ConnectionError. Таймаут: {timeout}сек.')
                    time.sleep(timeout)
                except requests.exceptions.HTTPError:
                    print(f'HTTPError. Проверьте урлы: текст = {book["url"]}, картинка = {book["img"]}.')

    pprint(team_books)
    books_json = json.dumps(team_books)

    with open("books.json", "w", encoding='utf8') as filejson:
        filejson.write(books_json)

if __name__ == "__main__":
    main()