# SERVER

FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

# [START system dependencies]
RUN apk add --update curl gcc g++ \
    && rm -rf /var/cache/apk/*

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# [START app environment]

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/


RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000