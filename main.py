import requests
from bs4 import BeautifulSoup
import urllib.parse


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
        url_components = urllib.parse.urlparse(url)
        return urllib.parse.urlunparse([url_components.scheme,url_components.netloc,path_url,'','',''])

def get_book_text(url):
    response = requests.get(url)
    response.raise_for_status()

    print(response.text)

def main():
    url_txt = get_text_url()
    get_book_text(url_txt)


if __name__ == "__main__":
    main()