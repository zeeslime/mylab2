FROM python:3.9.7

WORKDIR /fastapi-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["python", "./app/main.py"]