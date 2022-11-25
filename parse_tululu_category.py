from pprint import pprint
from pathlib import Path
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
    parser = argparse.ArgumentParser(description='Load books')
    parser.add_argument('--category', nargs='?', default='l55',
                        help='Categories of books. Default "l55".')
    parser.add_argument('--start_page', type=int, nargs='?', default=1,
                        help='Start page for download. Default 1.')
    parser.add_argument('--end_page', type=int, nargs='?', default=702,
                        help='End page for download, not included. Default 702.')
    parser.add_argument('--dest_folder',  nargs='?', default='',
                        help='Path to the directory with parsing results: pictures, books, JSON. '
                             'Default current dirictory.')
    parser.add_argument('--skip_imgs', action='store_true',
                        help='Used for not download pictures.')
    parser.add_argument('--skip_txt', action='store_true',
                        help='Used not download text.')
    parser.add_argument('--json_path', nargs='?', default='',
                        help='Path to the directory JSON file.'
                             'Default current dirictory.')

    return parser


def main():
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    books_category = command_line_arguments.category
    dest_folder = command_line_arguments.dest_folder
    start_page = command_line_arguments.start_page
    end_page = command_line_arguments.end_page
    skip_imgs = command_line_arguments.skip_imgs
    skip_txt = command_line_arguments.skip_txt
    json_path = command_line_arguments.json_path
    load_dotenv()

    books_directory = Path(dest_folder, os.environ['BOOKS_DIRECTORY'])
    images_directory = Path(dest_folder, os.environ['IMAGES_DIRECTORY'])
    site_url = os.environ['SITE_URL']

    timeout = 10
    pattern = re.compile(r'\d+')
    team_books = []

    for page in range(start_page, end_page):
        try:
            response = requests.get(urljoin(site_url, f"{books_category}/{page}/"))
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.TooManyRedirects:
            print(f'TooManyRedirects. Page = {page}, ошибочное перенаправление.')
            continue
        except requests.exceptions.ConnectionError:
            print(f'ConnectionError. Таймаут: {timeout}сек.')
            time.sleep(timeout)
            continue
        except requests.exceptions.HTTPError:
            print(f'HTTPError. Проверьте урлы: {response.url}.')
            continue

        site_members = urlparse(response.url)
        base_url = r"://".join([site_members.scheme, site_members.netloc])
        soup_result = BeautifulSoup(response.text, "html.parser")

        selector = "div#content table.d_book a"
        a_tags = soup_result.select(selector)

        for tag in a_tags:
            if not (tag.text == 'скачать книгу' or tag.text == 'читатели о книге'):
                continue

            url = urljoin(base_url, tag.get('href'))
            try:
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                url_components = urlparse(url)
                book_id = pattern.findall(url_components.path)[0]
                book = parse_book_page(response, book_id)
                payload = {"id": book_id}
                file_name = sanitize_filename(book['title'])
                if not skip_txt:
                    download_txt(f'{file_name}.txt', book['url'], payload, books_directory)
                if not skip_imgs:
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

    if json_path:
        filepath = Path(json_path, "books.json")
    else:
        filepath = Path(dest_folder, "books.json")

    with open(filepath, "w", encoding='utf8') as filejson:
        json.dump(team_books, filejson, ensure_ascii=False, indent=4, separators=(',', ':'))

if __name__ == "__main__":
    main()