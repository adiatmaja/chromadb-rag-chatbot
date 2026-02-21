@echo off
REM Docker Indexing Setup Script
REM This script runs all indexing tasks for first-time setup

echo ========================================
echo  Docker RAG System - First Time Setup
echo  Running Indexing Scripts
echo ========================================
echo.

REM Start container in detached mode
echo [1/5] Starting Docker container...
docker-compose up -d
echo.

REM Wait for container to be ready
echo [2/5] Waiting for container to initialize...
timeout /t 60 /nobreak
echo.

REM Index products
echo [3/5] Indexing product data...
docker exec rag-product-search python scripts/indexing/index_products.py
echo.

REM Parse and index intents
echo [4/5] Parsing and indexing intent data...
docker exec rag-product-search python scripts/indexing/parse_intent_data.py
docker exec rag-product-search python scripts/indexing/index_intent.py
echo.

REM Index FAQs (optional - requires ClickHouse)
echo [5/5] Indexing FAQ data (optional - skip if ClickHouse not available)...
docker exec rag-product-search python scripts/indexing/index_faq.py
echo.

REM Verify collections
echo ========================================
echo  Verifying Collections
echo ========================================
docker exec rag-product-search python -c "import sys; sys.path.insert(0, '/app/scripts'); from mock_onnxruntime import *; from src.core.retriever import UnifiedRetriever; r = UnifiedRetriever(); print(f'\nProducts: {r.product_collection.count()} items'); print(f'FAQs: {r.faq_collection.count()} items'); print(f'Intents: {r.intent_collection.count()} items'); print('\n✅ All collections ready!')"
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To test the system, run:
echo   docker-compose up
echo.
echo To stop the container:
echo   docker-compose down
echo.
pause
