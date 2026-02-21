# =============================================================================
# Optimized Dockerfile for RAG Product Search & Intent Classification System
# =============================================================================
# Single-stage build optimized for speed using pre-built binary wheels

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only (no build tools needed with binary wheels)
RUN apt-get update && apt-get install -y \
    curl \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel support
# This ensures we can use pre-built binary wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file first (for better layer caching)
COPY requirements.txt .

# Install heavy dependencies first with --only-binary to force wheel usage
# This dramatically speeds up the build (3-5 min vs 40 min)
RUN pip install --no-cache-dir \
    --only-binary=:all: \
    torch==2.8.0 \
    numpy==1.24.3 \
    scipy==1.13.0 \
    pandas==2.0.0 \
    scikit-learn==1.4.2 \
    transformers==4.57.1 \
    sentence-transformers==2.7.0 \
    || echo "Some packages don't have wheels, falling back to prefer-binary"

# Install remaining dependencies with prefer-binary as fallback
# Explicitly exclude onnxruntime to prevent Docker executable stack issues
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt && \
    pip uninstall -y onnxruntime || true

# Verify onnxruntime is not installed
RUN python -c "import sys; assert 'onnxruntime' not in sys.modules, 'onnxruntime should not be installed'" || echo "onnxruntime successfully excluded"

# Create necessary directories
RUN mkdir -p /app/data \
    /app/database/chroma_db \
    /app/logs

# Copy application code
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY data/ /app/data/
COPY .env.example /app/.env.example
COPY README.md /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # HuggingFace cache (replaces deprecated TRANSFORMERS_CACHE)
    HF_HOME=/app/.cache/huggingface \
    # Force sentence-transformers to use PyTorch instead of onnxruntime
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers \
    # Disable onnxruntime for sentence-transformers (use PyTorch backend)
    ST_DISABLE_ONNX=1 \
    # Default LLM configuration (can be overridden)
    LLM_BASE_URL=http://localhost:1234/v1 \
    LLM_MODEL_NAME=qwen2.5-7b-instruct \
    LLM_API_KEY=lm-studio \
    # Embedding configuration
    EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2 \
    # Vector DB configuration
    COLLECTION_NAME=fmcg_products \
    FAQ_COLLECTION_NAME=faq_collection \
    INTENT_COLLECTION_NAME=intent_collection \
    RETRIEVAL_TOP_K=3 \
    # LLM parameters
    LLM_TEMPERATURE=0.0 \
    LLM_MAX_TOKENS=1000 \
    # Logging
    LOG_LEVEL=INFO \
    ENABLE_RICH_CONSOLE=true

# Create a non-root user for security
RUN useradd -m -u 1000 raguser && \
    chown -R raguser:raguser /app

# Switch to non-root user
USER raguser

# Health check (optional - checks if the system can initialize)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from src.config import get_configuration_summary; get_configuration_summary()" || exit 1

# Volume mounts for persistence
# - /app/database: ChromaDB vector database
# - /app/data: Product data, intent data, stock data
# - /app/logs: Application logs (if implemented)
VOLUME ["/app/database", "/app/data", "/app/logs"]

# Default command: Run the interactive query system with onnxruntime mock
# Can be overridden with docker run command
CMD ["python", "scripts/docker_run_query.py"]
