FROM python:3.11.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache

COPY . .


CMD alembic upgrade head; python src/main.py