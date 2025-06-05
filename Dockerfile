FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry без создания виртуального окружения
RUN pip install --upgrade pip && \
    pip install poetry==1.8.2 && \
    poetry config virtualenvs.create false

# Копируем только файлы зависимостей сначала
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-ansi --only main

# Копируем остальной код
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python3", "bot/main.py"]

