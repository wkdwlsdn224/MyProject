# 1. 베이스 이미지
FROM python:3.12-slim

# 2. 작업 디렉터리 설정
WORKDIR /app

# 3. 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 코드 복사
COPY . .

# 5. 환경 변수 (빌드 시 값 주입 or .env 사용)
ENV PYTHONUNBUFFERED=1

# 6. 애플리케이션 실행
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
