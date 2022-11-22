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
    start_page = 1
    end_page = 4
    pattern = re.compile(r'\d+')
    team_books=[]

    for page in range(start_page, end_page + 1):
        response = requests.get(urljoin(site_url, f"{books_category}/{page}/"))
        response.raise_for_status()
        soup_result = BeautifulSoup(response.text, "html.parser")
        div_id_content_part = soup_result.body.find('div', attrs={'id': 'content'})

        table_class_d_book_part = div_id_content_part.findAll('table', attrs={'class': 'd_book'})

        for part_book in table_class_d_book_part:
            found_urls = part_book.findAll('a')

            url = ''
            for tag in found_urls:
                if tag.text == 'скачать книгу' or tag.text == 'читатели о книге':
                    url = urljoin(site_url, tag.get('href'))
                    break
            if not url:
                raise WrongUrl

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
            # finally:
            #     print()
    pprint(team_books)
    books_json = json.dumps(team_books)

    with open("books.json", "w", encoding='utf8') as filejson:
        filejson.write(books_json)

if __name__ == "__main__":
    main()