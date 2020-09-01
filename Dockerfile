FROM python:3.7.4-alpine3.9

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["/app/bot_table.py"]