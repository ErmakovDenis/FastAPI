# Используем официальный образ Python, который содержит последнюю версию Python
FROM python:3.10

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы в рабочую директорию
COPY . .

# Экспортируем порт, который будет использоваться приложением
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
