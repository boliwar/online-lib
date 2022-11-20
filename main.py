import requests
import requests.exceptions
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from dotenv import load_dotenv
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse, urlunparse


def get_text_url(url='http://tululu.org/b32168/', find_txt='скачать txt'):
    response = requests.get(url)
    response.raise_for_status()
    bs_result = BeautifulSoup(response.text, "html.parser")
    download_panel = bs_result.body.findAll('a',)

    path_url = ''
    for teg in download_panel:
        if teg.text == find_txt:
            path_url = teg.get("href")
            break

    if path_url:
        url_components = urlparse(url)
        return urlunparse([url_components.scheme,url_components.netloc,path_url,'','',''])

def  create_team_books(site_url, firs_id=1, last_id=10):
    team_books = []
    for i in range(firs_id, last_id + 1):
        try:
            team_books.append(get_struct_book_by_id(i, site_url))
        except requests.exceptions.TooManyRedirects:
            pass
    return team_books

def get_struct_book_by_id(id, site_url):
    response = requests.get(urljoin(site_url,f"b{str(id)}"))
    response.raise_for_status()
    check_for_redirect(response)
    bs_result = BeautifulSoup(response.text, "html.parser")
    books_result = bs_result.body.find('div', attrs={'id': 'content'})
    bs_result = BeautifulSoup('<html>'+str(books_result)+'</html>', "html.parser")
    img_struct = bs_result.find('img')
    title_str = bs_result.find('h1')

    return {'index': str(id),
            'title': f"{id}. {title_str.text.split('::')[0].strip()}",
            'img': urljoin(site_url,img_struct.get("src")),
            }


def get_team_books(url, count, site_url):
    response = requests.get(url)
    response.raise_for_status()
    bs_result = BeautifulSoup(response.text, "html.parser")
    books_result = bs_result.body.findAll('div', attrs={'class': 'bookimage'} )
    team_books = []
    i = 0
    for book_struct in books_result:
        struct = BeautifulSoup('<html>'+str(book_struct)+'</html>', "html.parser")
        book_params = struct.find('a')
        img_struct = BeautifulSoup('<html>'+str(book_params)+'</html>', "html.parser")
        img_params = img_struct.find('img')
        team_books.append({'index': book_params.get("href"),
                           'title': book_params.get("title"),
                           'img': urljoin(site_url, img_params.get("src")),
                           })
        i =+ 1
        if i >= count: break
    return team_books


def save_book(book, directory_books, download_url, directory_images):
    pattern = re.compile(r'\d+')
    book_id = pattern.findall(book['index'])[0]
    payload = {"id": book_id}
    file_name = sanitize_filename(book['title'])
    try:
        return download_txt(f'{file_name}.txt', download_url, payload, directory_books), \
               download_image(book['img'], None, directory_images)

    except requests.exceptions.TooManyRedirects:
        pass


def check_for_redirect(response):
    if response.history and response.url=='https://tululu.org/':
        raise requests.exceptions.TooManyRedirects

def download_txt(file_name, url, payload=None ,directory_books='books/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    directory_book = Path(os.getcwd(),directory_books)
    directory_book.mkdir(parents=True, exist_ok=True)

    with open(Path(directory_book, file_name), 'wb') as file:
        file.write(response.content)

    return Path(directory_book, file_name)

def download_image(url, payload=None ,directory_images='images/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    directory_book = Path(os.getcwd(),directory_images)
    directory_book.mkdir(parents=True, exist_ok=True)

    url_components = urlparse(url)
    file_path, file_name = os.path.split(url_components.path)

    with open(Path(directory_images, file_name), 'wb') as file:
        file.write(response.content)

    return Path(directory_book, file_name)


def main():
    load_dotenv()
    directory_books = os.environ['DIRECTORY_BOOKS']
    directory_images = os.environ['DIRECTORY_IMAGES']
    books_count = int(os.environ['BOOKS_COUNT'])
    site_url = os.environ['SITE_URL']
    books_team_url = urljoin(site_url,os.environ['BOOKS_TEAM_URL'])
    download_url = urljoin(site_url,os.environ['DOWNLOAD_URL'])

    # team_books = get_team_books(books_team_url, books_count, site_url)
    team_books = create_team_books(site_url)
    for book in team_books:
        print(save_book(book, directory_books, download_url, directory_images))

if __name__ == "__main__":
    main()