import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
from dotenv import load_dotenv
from pathlib import Path
import re


def get_team_books(url, count):
    response = requests.get(url)
    response.raise_for_status()
    bs_result = BeautifulSoup(response.text, "html.parser")
    books_result = bs_result.body.findAll('div', attrs={'class': 'bookimage'} )
    team_books = []
    i = 0
    for book_struct in books_result:
        struct = BeautifulSoup('<html>'+str(book_struct)+'</html>', "html.parser")
        book_params = struct.find('a')
        team_books.append({'index':book_params.get("href"), 'title': book_params.get("title")})
        i =+ 1
        if i >= count: break

    return team_books

def save_books(books_team_url, books_count, directory_books, download_url):
    pattern = re.compile(r'\d+')
    team_books = get_team_books(books_team_url, books_count)
    for book in team_books:
        book_id = pattern.findall(book['index'])[0]
        payload = {"id": book_id}
        save_book_text(download_url, payload, directory_books, f'book_{book_id}.txt')


def save_book_text(url, payload ,directory_books, file_name):
    response = requests.get(url, params=payload)
    response.raise_for_status()

    directory_book = Path(os.getcwd(),directory_books)
    directory_book.mkdir(parents=True, exist_ok=True)
    print(Path(directory_book, file_name))
    with open(Path(directory_book, file_name), 'wb') as file:
        file.write(response.content)


def main():
    load_dotenv()
    directory_books = os.environ['DIRECTORY_BOOKS']
    books_count = int(os.environ['BOOKS_COUNT'])
    books_team_url = os.environ['BOOKS_TEAM_URL']
    download_url = os.environ['DOWNLOAD_URL']
    save_books(books_team_url, books_count, directory_books, download_url)

if __name__ == "__main__":
    main()