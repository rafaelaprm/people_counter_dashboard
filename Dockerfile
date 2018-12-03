FROM python:3.6

RUN mkdir /app
COPY . /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
