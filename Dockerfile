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

# 파이썬 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --upgrade --force-reinstall -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

ENV PYTHONUNBUFFERED=1

# FastAPI + bot 루프를 main.py에서 같이 기동
CMD ["python", "main.py"]
