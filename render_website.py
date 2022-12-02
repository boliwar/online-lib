from jinja2 import Environment, FileSystemLoader, select_autoescape
from parse_tululu_category import create_parser
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from livereload import Server
from pathvalidate import sanitize_filename
from more_itertools import chunked


def rebuild(books):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    pages_directory = Path(os.getcwd(), 'pages')
    pages_directory.mkdir(parents=True, exist_ok=True)

    count_per_page = 15
    parts_by_page = list(chunked(books, count_per_page))
    pages_count = len(parts_by_page)
    for current_page, part_page in enumerate(parts_by_page, 1):
        rendered_page = template.render(
                                        books=part_page,
                                        pages_count=pages_count,
                                        current_page=current_page,
                                       )
        with open(Path(pages_directory, f'index{current_page}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    books = []
    parser = create_parser()
    command_line_arguments = parser.parse_args()
    dest_folder = command_line_arguments.dest_folder

    load_dotenv()

    books_directory = Path('../', dest_folder, os.environ['BOOKS_DIRECTORY'])
    images_directory = Path('../', dest_folder, os.environ['IMAGES_DIRECTORY'])

    filepath = Path(dest_folder, "books.json")

    with open(filepath, "r", encoding='utf8') as filejson:
        books = json.load(filejson)

    for book in books:
        book['img'] = str(Path(images_directory, os.path.basename(urlparse(book['img']).path))).replace(os.sep, '/')
        book['url'] = str(Path(books_directory, f'{sanitize_filename(book["title"])}.txt')).replace(os.sep, '/')

    rebuild(books)
    server = Server()
    server.watch('template.html', rebuild(books))
    server.serve(default_filename=r'./pages/index1.html')


if __name__ == "__main__":
    main()
