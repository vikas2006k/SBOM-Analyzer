FROM python:3.12-slim

WORKDIR /app

# Install system packages required for some python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV APP_ENV=production
ENV PORT=5000

CMD ["python", "wsgi.py"]
