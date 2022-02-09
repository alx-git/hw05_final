# YATUBE

ОПИСАНИЕ
---

Учебный проект социальной сети Yatube, созданный в Django, с управлением пользователями, версткой, базой данных постов, формами, возможностью подписаться на авторов и т.д. Также, для тренировки, были написаны тесты для покрытия моделей, forms, views и urls.

ЗАВИСИМОСТИ
---
Django==2.2.16

mixer==7.1.2

Pillow==8.3.1

pytest==6.2.4

pytest-django==4.4.0

pytest-pythonpath==0.7.3

requests==2.26.0

six==1.16.0

sorl-thumbnail==12.7.0

УСТАНОВКА
---

Клонировать репозиторий и перейти в него в командной строке:

git clone

cd hw05_final

Cоздать и активировать виртуальное окружение:

python -m venv venv

source venv/Scripts/activate

Установить зависимости из файла requirements.txt:

pip install -r requirements.txt

Выполнить миграции:

python manage.py migrate

Запустить проект:

python manage.py runserver
