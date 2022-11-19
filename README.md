# Библиотека книг оффлайн
# скачиваем книги с сайта  [https://tululu.org/](https://tululu.org/)

### Запуск программы:
Выполняется из командной строки в каталоге размещения.
```
python main.py
```
возвращает в консоль две таблицы 
со статистикой по самым популярным языкам программирования и среднюю зарплату


### Как установить
Необходимо создать файл окружения .env в каталоге программы.
В файле с помощью редактора указать переменную окружения: 
```
DIRECTORY_BOOKS=
BOOKS_COUNT=
BOOKS_TEAM_URL=
DOWNLOAD_URL=
```
Токен необходимо получить в службе [API SuperJobs](https://api.superjob.ru/).

Python3 должен быть уже установлен. Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Рекомендуется использовать [виртуальное окружение](https://docs.python.org/3/library/venv.html) для изоляции проекта. 

### Цель проекта
Код написан в целях знакомства с Api указанных сайтов.
