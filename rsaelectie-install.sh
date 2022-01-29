#!/bin/bash
git clone https://github.com/tp17-2021/rsa-library.git
cd rsa-library
git checkout development
python3 setup.py bdist_wheel
pip install dist/rsaelectie-0.1-py3-none-any.whl
cd ..