# Використовуємо офіційний легкий образ Python
FROM python:3.10-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлюємо системні залежності
# (для mysqlclient та reportlab)
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    fonts-freefont-ttf \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей та ВСТАНОВЛЮЄМО ЇХ
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копіюємо весь код проєкту в робочу директорію
COPY . .
