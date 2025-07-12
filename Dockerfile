# Python 3.10 slim 베이스
FROM python:3.10-slim

WORKDIR /app

# 최소 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
  && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --upgrade --force-reinstall -r requirements.txt

# 코드 복사
COPY . .

ENV PYTHONUNBUFFERED=1

# main.py 에서 FastAPI + bot 루프를 동시에 띄우도록 작성했기 때문에
# 이 한 줄만 있으면 됩니다.
CMD ["python", "main.py"]
