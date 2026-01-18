# Research Assistant Docker Image
# Level 17: Multi-agent research system with Semantic Scholar integration
#
# Build: docker build -t research-assistant .
# Run:   docker run -it --env-file .env research-assistant

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    # Default data directory inside container
    RESEARCH_DATA_DIR=/app/data

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For PDF generation
    libfontconfig1 \
    # For general utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash researcher
RUN mkdir -p /app/data && chown -R researcher:researcher /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=researcher:researcher 17_research_assistant_semantic_scholar.py ./researchassistant.py

# Copy entrypoint script
COPY --chown=researcher:researcher docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER researcher

# Create data directories
RUN mkdir -p /app/data/pdfs \
             /app/data/diagrams \
             /app/data/exports \
             /app/data/obsidian_vault

# Volume for persistent data
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import anthropic; print('OK')" || exit 1

# Default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "researchassistant.py"]
