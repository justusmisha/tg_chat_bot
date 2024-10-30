FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем необходимые файлы
COPY requirements.txt /app/requirements.txt

# Устанавливаем необходимые пакеты
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем сервер FastAPI с помощью uvicorn
CMD ["python3", "main.py"]