from jinja2 import Environment, FileSystemLoader, select_autoescape
from http.server import HTTPServer, SimpleHTTPRequestHandler
from parse_tululu_category import create_parser
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse

def main():
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    dest_folder = command_line_arguments.dest_folder


    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    load_dotenv()

    books_directory = Path(dest_folder, os.environ['BOOKS_DIRECTORY'])
    images_directory = Path(dest_folder, os.environ['IMAGES_DIRECTORY'])

    template = env.get_template('template.html')

    filepath = Path(dest_folder, "books.json")

    with open(filepath, "r", encoding='utf8') as filejson:
        books_json = filejson.read()

    books = json.loads(books_json)

    for book in books:
        book['img'] = Path(images_directory,os.path.basename(urlparse(book['img']).path))

    rendered_page = template.render(books=books,)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()