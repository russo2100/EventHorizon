FROM python:3.11-slim

WORKDIR /app

COPY requirements.app.txt /app/requirements.app.txt
RUN pip install --no-cache-dir -r /app/requirements.app.txt


COPY . .

EXPOSE 8000
CMD ["python", "-m", "src.api.main"]
