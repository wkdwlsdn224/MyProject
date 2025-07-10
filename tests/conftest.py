# tests/conftest.py
import os
import sys

# 이 파일(tests/conftest.py)의 부모 폴더(=프로젝트 루트)를 sys.path에 추가
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)
