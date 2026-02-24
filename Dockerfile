# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt gunicorn

RUN useradd --create-home appuser
USER appuser

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
