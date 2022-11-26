from jinja2 import Environment, FileSystemLoader, select_autoescape
from http.server import HTTPServer, SimpleHTTPRequestHandler
from parse_tululu_category import create_parser
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from livereload import Server

books = []

def rebuild():
    global books
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(books=books,)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    print("Site rebuilt")


def main():
    global books
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    dest_folder = command_line_arguments.dest_folder

    load_dotenv()

    books_directory = Path(dest_folder, os.environ['BOOKS_DIRECTORY'])
    images_directory = Path(dest_folder, os.environ['IMAGES_DIRECTORY'])

    filepath = Path(dest_folder, "books.json")

    with open(filepath, "r", encoding='utf8') as filejson:
        books_json = filejson.read()

    books = json.loads(books_json)

    for book in books:
        book['img'] = Path(images_directory,os.path.basename(urlparse(book['img']).path))

    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve()

if __name__ == "__main__":
    main()