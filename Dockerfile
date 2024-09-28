FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential sqlite3 vim procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/luigi-server/
RUN chmod 777 /var/lib/luigi-server/

# Directory for Luigi logs
RUN mkdir /var/log/luigi

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set up database
RUN sqlite3 /app/expenses.db < /app/ddl/expenses.sql

# Expose Luigi's web server port
EXPOSE 8082

# Run Luigi service
CMD ["luigid", "--port", "8082"] 
