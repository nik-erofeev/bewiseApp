#!/bin/bash


# export env
POSTGRES_HOST=${DB__HOST}
POSTGRES_PORT=${DB__PORT}
KAFKA_PORT=${KAFKA__PORT:-9092}

echo "Waiting for PostgreSQL to start..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done



echo "Starting migrations..."
alembic upgrade head


echo Check migration status
MIGRATION_STATUS=$?
if [ $MIGRATION_STATUS -ne 0 ]; then
  echo "Migrations failed with status $MIGRATION_STATUS"
  exit 1
fi

echo "Waiting for Kafka to start on port $KAFKA_PORT..."
while ! nc -z kafka "$KAFKA_PORT"; do
  sleep 1
done


echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload