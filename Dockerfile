FROM python:3.10-alpine

WORKDIR /code

RUN apk add -U g++ gcc git bash

COPY ./data ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./rsaelectie-install.sh ./rsaelectie-install.sh

RUN ./rsaelectie-install.sh

COPY ./src /code/src

CMD [ "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "80" ]