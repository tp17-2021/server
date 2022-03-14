#!/bin/bash
python3 /code/tests/seeder.py

while ! nc -z electie_test_es_01 9200; do
    echo "Waiting for ES to start";
    sleep 2;
done;

echo "Curl checking for ES green status start"
curl -X GET "electie_test_es_01:9200/_cluster/health?wait_for_status=green&timeout=50s"
echo "ES green status reached"

pytest -srP --verbose --asyncio-mode=strict --disable-pytest-warnings
