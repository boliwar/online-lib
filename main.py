import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from dotenv import load_dotenv
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
import argparse


class WrongUrl(Exception):
    """Raised when empty url"""
    pass

def create_books_team(site_url, firs_id=1, last_id=10):
    books_team = []
    for i in range(firs_id, last_id + 1):
        try:
            books_team.append(parse_book_page(i, site_url))
        except requests.exceptions.TooManyRedirects:
            pass
        except WrongUrl:
            pass

    return books_team


def parse_book_page(book_id, site_url):
    response = requests.get(urljoin(site_url, f"b{str(book_id)}"))
    response.raise_for_status()
    check_for_redirect(response)
    bs_result = BeautifulSoup(response.text, "html.parser")
    books_result = bs_result.body.find('div', attrs={'id': 'content'})

    urls_result = bs_result.body.find('table', attrs={'class': 'd_book'})
    urls_result = BeautifulSoup('<html>'+str(urls_result)+'</html>', "html.parser")
    urls_result = urls_result.findAll('a')
    url = ''
    for tag in urls_result:
        if tag.text == 'скачать txt':
            url = tag.get('href')
            break
    if url:
        url = urljoin(site_url, url)
    else:
        raise WrongUrl

    comments_result = bs_result.body.findAll('div', attrs={'class': 'texts'})
    comments_result = BeautifulSoup('<html>'+str(comments_result)+'</html>', "html.parser")
    comments_result = comments_result.findAll('span')

    genres_result = bs_result.body.findAll('span', attrs={'class': 'd_book'})
    genres_result = BeautifulSoup('<html>'+str(genres_result)+'</html>', "html.parser")
    genres_result = genres_result.findAll('a')

    bs_result = BeautifulSoup('<html>'+str(books_result)+'</html>', "html.parser")
    img_struct = bs_result.find('img')
    title_str = bs_result.find('h1')

    return {'index': str(book_id),
            'url': url,
            'title': f"{book_id}. {title_str.text.split('::')[0].strip()}",
            'author': title_str.text.split('::')[1].strip(),
            'img': urljoin(site_url, img_struct.get("src")),
            'comments': [comment.text for comment in comments_result],
            'genres': [genre.text for genre in genres_result],
            }


def save_book(book, directory_books,  directory_images):
    pattern = re.compile(r'\d+')
    book_id = pattern.findall(book['index'])[0]
    payload = {"id": book_id}
    file_name = sanitize_filename(book['title'])
    download_txt(f'{file_name}.txt', book['url'], payload, directory_books)
    download_image(book['img'], None, directory_images)


def check_for_redirect(response):
    if response.history and response.url == 'https://tululu.org/':
        raise requests.exceptions.TooManyRedirects


def download_txt(file_name, url, payload=None, directory_books='books/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    directory_book = Path(os.getcwd(), directory_books)
    directory_book.mkdir(parents=True, exist_ok=True)

    with open(Path(directory_book, file_name), 'wb') as file:
        file.write(response.content)

    return Path(directory_book, file_name)


def download_image(url, payload=None, directory_images='images/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    directory_book = Path(os.getcwd(), directory_images)
    directory_book.mkdir(parents=True, exist_ok=True)

    url_components = urlparse(url)
    file_path, file_name = os.path.split(url_components.path)

    with open(Path(directory_images, file_name), 'wb') as file:
        file.write(response.content)

    return Path(directory_book, file_name)


def create_parser():
    parser = argparse.ArgumentParser(description='Bot for load images to Telegram channel')
    parser.add_argument('--start_id', type=int, nargs='?', default=1,
                        help='Book ID to start with. Default 1.')
    parser.add_argument('--end_id', type=int, nargs='?', default=10,
                        help='Book ID to end with. Default 10.')
    return parser


def main():
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    start_id = command_line_arguments.start_id
    end_id = command_line_arguments.end_id
    load_dotenv()
    directory_books = os.environ['DIRECTORY_BOOKS']
    directory_images = os.environ['DIRECTORY_IMAGES']
    site_url = os.environ['SITE_URL']


    books_team = create_books_team(site_url, start_id, end_id)
    for book in books_team:
        save_book(book, directory_books, directory_images)
        print(book)


if __name__ == "__main__":
    main()
