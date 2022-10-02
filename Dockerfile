FROM python:3.10.6-slim

WORKDIR /usr/src/app

COPY ./requirements.txt ./

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copying application files
COPY ./src/. .

# watch app' files
ENV FLASK_APP=flaskr
ENV FLASK_DEBUG=True
ENV FLASK_ENV=development

CMD ["sh", "-c", "python -m flask run --host=0.0.0.0"]

