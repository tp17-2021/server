FROM python:3.10-alpine as base

WORKDIR /code

RUN apk add -U g++ gcc git bash

COPY ./data ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./rsaelectie-install.sh ./rsaelectie-install.sh

RUN ./rsaelectie-install.sh

COPY ./src /code/src

FROM base as test
CMD ["pytest", "-rP", "--verbose"]
# magic command bellow:
# docker-compose -f docker-compose.test.yml up --build --exit-code-from server

FROM base as build
CMD [ "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "80" ]
