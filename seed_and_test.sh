#!/bin/bash
python3 /code/tests/seeder.py
pytest -srP --verbose --asyncio-mode=strict