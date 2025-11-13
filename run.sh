#!/bin/bash
# Quick start script for the English Teachers Library

echo "Starting English Teachers Library..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found!"
    echo "Please ensure .env file exists with database configuration."
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PostgreSQL Docker container is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Warning: PostgreSQL is not running!"
    echo "Start it with: cd Docker && docker compose up -d"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Database connection ready"
echo "✓ Starting Streamlit application..."
echo ""

# Activate poetry environment and run streamlit
poetry run streamlit run app/main.py
