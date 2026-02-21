@echo off
REM =============================================================================
REM Quick Docker Rebuild Script for Windows
REM =============================================================================
REM This script rebuilds the Docker image and tests it

echo ========================================
echo Docker Rebuild Script
echo ========================================
echo.

REM Stop any running containers
echo [1/5] Stopping existing containers...
docker-compose down
echo.

REM Build the image (should take 3-5 min now, or use cache if nothing changed)
echo [2/5] Building Docker image...
echo This may take a few minutes on first build...
docker-compose build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker build failed!
    exit /b 1
)
echo.

REM Test the mock
echo [3/5] Testing onnxruntime mock...
docker-compose run --rm rag python scripts/test_docker_mock.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Mock test failed!
    exit /b 1
)
echo.

REM List installed packages (verify onnxruntime is NOT installed)
echo [4/5] Verifying onnxruntime is excluded...
docker-compose run --rm rag pip list | findstr /C:"onnxruntime"
if %ERRORLEVEL% EQU 0 (
    echo WARNING: onnxruntime is still installed!
) else (
    echo SUCCESS: onnxruntime successfully excluded!
)
echo.

REM Show image info
echo [5/5] Docker image info:
docker images rag-product-search:latest
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start the container:  docker-compose up
echo   2. Index data (first time only):
echo      docker-compose exec rag python scripts/indexing/index_products.py
echo      docker-compose exec rag python scripts/indexing/index_intent.py
echo.

pause
