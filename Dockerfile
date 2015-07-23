FROM python:2.7
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

COPY . /code

RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput 