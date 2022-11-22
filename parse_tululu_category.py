import requests
import main
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import argparse

class WrongUrl(Exception):
    """Raised when empty url"""
    pass

def create_parser():
    parser = argparse.ArgumentParser(description='Bot for load images to Telegram channel')
    parser.add_argument('--category', nargs='?', default='fantastic',
                        help='Categories of books. Default "fantastic".')
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

    book = {}
    response = requests.get(urljoin(site_url, f"{books_category}/"))
    response.raise_for_status()
    soup_result = BeautifulSoup(response.text, "html.parser")
    div_id_content_part = soup_result.body.find('div', attrs={'id': 'content'})

    table_class_d_book_part = div_id_content_part.findAll('table', attrs={'class': 'd_book'})

    for book in table_class_d_book_part:
        found_urls = book.findAll('a')

        url = ''
        for tag in found_urls:
            if tag.text == 'скачать книгу':
                url = urljoin(site_url, tag.get('href'))
                break
        # if not url:
        #     raise WrongUrl

        print(url)

if __name__ == "__main__":
    main()