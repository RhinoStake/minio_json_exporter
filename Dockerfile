# syntax=docker/dockerfile:1

FROM python:3-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt gunicorn

FROM python:3-alpine

WORKDIR /app

COPY --from=builder /install /usr/local

RUN adduser -D appuser
ENV TMPDIR=/home/appuser
USER appuser

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
