FROM python:3.10-alpine

WORKDIR /code

COPY ./data ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./src /code/src

CMD [ "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "80" ]
