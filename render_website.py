from jinja2 import Environment, FileSystemLoader, select_autoescape
from http.server import HTTPServer, SimpleHTTPRequestHandler
from parse_tululu_category import create_parser
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from livereload import Server
from pathvalidate import sanitize_filename
from more_itertools import chunked

books = []

def rebuild():
    global books
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    pages_directory = Path(os.getcwd(), 'pages')
    pages_directory.mkdir(parents=True, exist_ok=True)

    parts_by_page = list(chunked(books, 15))
    pages_count = (len(parts_by_page))
    for i, part_page in enumerate(parts_by_page, 1):
        rendered_page = template.render(
                                        books=part_page,
                                        pages_count = pages_count,
                                        current_page=i,
                                       )
        with open(Path(pages_directory, f'index{i}.html'), 'w', encoding="utf8") as file:
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
        book['img'] = Path('../', images_directory, os.path.basename(urlparse(book['img']).path))
        book['url'] = Path('../', books_directory, f'{sanitize_filename(book["title"])}.txt')

    rebuild()
    # server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    # server.serve_forever()

    server = Server()
    server.watch('template.html', rebuild)
    server.serve(default_filename=r'./pages/index1.html')

if __name__ == "__main__":
    main()