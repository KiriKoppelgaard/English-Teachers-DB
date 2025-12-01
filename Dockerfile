# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY TeacherLibrary/ ./TeacherLibrary/
COPY app/ ./app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    streamlit>=1.31.0 \
    sqlalchemy>=2.0.25 \
    psycopg2-binary>=2.9.9 \
    pydantic>=2.5.3 \
    python-dotenv>=1.0.0 \
    pandas>=2.1.4 \
    openpyxl>=3.1.2 \
    requests>=2.31.0 \
    sentence-transformers>=2.2.0 \
    scikit-learn>=1.3.0

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
ENTRYPOINT ["streamlit", "run", "app/🏠_Hjem.py", "--server.port=8501", "--server.address=0.0.0.0"]
