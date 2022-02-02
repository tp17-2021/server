#!/bin/bash
python3 /code/src/tests/seeder.py
pytest -srP --verbose --asyncio-mode=strict