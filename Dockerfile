FROM python:3.10-alpine as base

WORKDIR /code

RUN apk add -U g++ gcc git bash

COPY ./data ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./rsaelectie-install.sh ./rsaelectie-install.sh

RUN chmod a+x rsaelectie-install.sh

RUN ./rsaelectie-install.sh

COPY ./src /code/src

COPY ./tests /code/tests

FROM base as test

COPY ./seed_and_test.sh ./seed_and_test.sh

RUN chmod a+x seed_and_test.sh

CMD ["./seed_and_test.sh"]
# magic command bellow:
# docker-compose -f docker-compose.test.yml up --build --exit-code-from server --force-recreate

FROM base as build
CMD [ "uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "80" ]
