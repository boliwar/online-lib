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

def create_team_book(site_url, current_id):
    response = requests.get(urljoin(site_url, f"b{str(current_id)}"))
    response.raise_for_status()
    check_for_redirect(response)
    return parse_book_page(response, site_url, current_id)


def parse_book_page(response, site_url, book_id):

    bs_result = BeautifulSoup(response.text, "html.parser")
    books_result = bs_result.body.find('div', attrs={'id': 'content'})

    title_str = bs_result.body.find('h1')
    title, author = title_str.text.split('::')
    img_struct = bs_result.body.find('div', attrs={'class': 'bookimage'})
    img_struct = img_struct.find('img')

    urls_result = books_result.find('table', attrs={'class': 'd_book'})
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
    genres_result = bs_result.body.findAll('span', attrs={'class': 'd_book'})


    return {'index': str(book_id),
            'url': url,
            'title': f"{book_id}. {title.strip()}",
            'author': author.strip(),
            'img': urljoin(site_url, img_struct.get("src")),
            'comments': [comment.text for comments in comments_result for comment in comments.find('span')],
            'genres': [genre.text for genres in genres_result for genre in genres.findAll('a')],
            }


def save_book(book, books_directory,  images_directory):
    pattern = re.compile(r'\d+')
    book_id = pattern.findall(book['index'])[0]
    payload = {"id": book_id}
    file_name = sanitize_filename(book['title'])
    download_txt(f'{file_name}.txt', book['url'], payload, books_directory)
    download_image(book['img'], None, images_directory)


def check_for_redirect(response):
    if response.history and response.url == 'https://tululu.org/':
        raise requests.exceptions.TooManyRedirects


def download_txt(file_name, url, payload=None, books_directory='books/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    book_directory = Path(os.getcwd(), books_directory)
    book_directory.mkdir(parents=True, exist_ok=True)

    with open(Path(book_directory, file_name), 'wb') as file:
        file.write(response.content)

    return Path(book_directory, file_name)


def download_image(url, payload=None, images_directory='images/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    image_directory = Path(os.getcwd(), images_directory)
    image_directory.mkdir(parents=True, exist_ok=True)

    url_components = urlparse(url)
    file_path, file_name = os.path.split(url_components.path)

    with open(Path(images_directory, file_name), 'wb') as file:
        file.write(response.content)

    return Path(images_directory, file_name)


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
    books_directory = os.environ['BOOKS_DIRECTORY']
    images_directory = os.environ['IMAGES_DIRECTORY']
    site_url = os.environ['SITE_URL']

    books_team = []
    for current_id in range(start_id, end_id + 1):
        try:
            books_team.append(create_team_book(site_url, current_id))
        except requests.exceptions.TooManyRedirects:
            pass
        except WrongUrl:
            pass

    for book in books_team:
        save_book(book, books_directory, images_directory)
        print(f"Название: {book['title']}")
        print(f"Автор: {book['author']}")
        print()


if __name__ == "__main__":
    main()
