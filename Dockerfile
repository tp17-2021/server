FROM python:3.10-alpine

WORKDIR /code

RUN apk add -U g++ gcc

COPY ./data ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./src /code/src

COPY ./testing.py /code/testing.py

CMD [ "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "80" ]
