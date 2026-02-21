@echo off
REM Quick Docker verification script

echo ================================
echo Docker RAG System Verification
echo ================================
echo.

REM Check Docker
echo [1/8] Checking Docker installation...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    exit /b 1
)
docker --version
echo.

REM Check image
echo [2/8] Checking Docker image...
docker images | findstr rag-product-search >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Image not found. Run: deploy.bat build
) else (
    docker images | findstr rag-product-search
)
echo.

REM Check container status
echo [3/8] Checking container status...
docker ps -a | findstr rag-product-search >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Container not created yet.
) else (
    docker ps -a | findstr rag-product-search
)
echo.

REM Check volumes
echo [4/8] Checking data volumes...
if exist "database\" (
    echo [OK] database/ directory exists
) else (
    echo [WARNING] database/ directory not found
)
if exist "data\" (
    echo [OK] data/ directory exists
) else (
    echo [WARNING] data/ directory not found
)
echo.

REM Check .env file
echo [5/8] Checking configuration...
if exist ".env" (
    echo [OK] .env file exists
) else (
    echo [WARNING] .env file not found. Copy from .env.example
)
echo.

REM If container is running, test it
echo [6/8] Testing container (if running)...
docker ps | findstr rag-product-search >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Container is running. Running quick test...
    docker-compose exec -T rag python -c "from src.core.retriever import UnifiedRetriever; print('✓ Imports OK')"
    if %ERRORLEVEL% equ 0 (
        echo [OK] Container imports working
    )
) else (
    echo [INFO] Container not running. Start with: deploy.bat start
)
echo.

REM Check data files
echo [7/8] Checking required data files...
if exist "data\stock_data.csv" (
    echo [OK] stock_data.csv exists
) else (
    echo [ERROR] stock_data.csv missing!
)
if exist "data\product_data.csv" (
    echo [OK] product_data.csv exists
) else (
    echo [ERROR] product_data.csv missing!
)
if exist "data\intent_data.csv" (
    echo [OK] intent_data.csv exists
) else (
    echo [WARNING] intent_data.csv not found (will be created during indexing)
)
echo.

REM Summary
echo [8/8] Summary
echo ================================
echo.
echo Next steps:
echo   1. If image not built: deploy.bat build
echo   2. If not running:     deploy.bat start
echo   3. First time setup:   deploy.bat index
echo   4. Test stock reader:  deploy.bat test
echo   5. View logs:          deploy.bat logs
echo.
