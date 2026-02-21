@echo off
REM =============================================================================
REM Docker Deployment Helper Script for RAG Product Search System (Windows)
REM =============================================================================
REM This script helps manage Docker deployment with common operations on Windows.
REM
REM Usage:
REM   deploy.bat build      # Build Docker image
REM   deploy.bat start      # Start container
REM   deploy.bat stop       # Stop container
REM   deploy.bat restart    # Restart container
REM   deploy.bat logs       # View logs
REM   deploy.bat shell      # Access container shell
REM   deploy.bat index      # Index all data
REM   deploy.bat status     # Check container status
REM   deploy.bat clean      # Clean up containers and images

setlocal enabledelayedexpansion

REM Container and image names
set CONTAINER_NAME=rag-product-search
set IMAGE_NAME=rag-product-search:latest

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Main command dispatcher
if "%1"=="" goto :usage
if /i "%1"=="build" goto :build
if /i "%1"=="start" goto :start
if /i "%1"=="stop" goto :stop
if /i "%1"=="restart" goto :restart
if /i "%1"=="logs" goto :logs
if /i "%1"=="shell" goto :shell
if /i "%1"=="index" goto :index_data
if /i "%1"=="status" goto :status
if /i "%1"=="demo" goto :demo
if /i "%1"=="test" goto :test_stock
if /i "%1"=="clean" goto :clean
if /i "%1"=="help" goto :usage
goto :usage

:build
echo [INFO] Building Docker image: %IMAGE_NAME%
docker build -t %IMAGE_NAME% .
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Docker image built successfully
) else (
    echo [ERROR] Build failed
    exit /b 1
)
goto :end

:start
if not exist .env (
    echo [WARNING] .env file not found
    if exist .env.example (
        echo [INFO] Creating .env from .env.example
        copy .env.example .env
        echo [SUCCESS] .env file created. Please edit it with your configuration.
        echo [WARNING] Deployment paused. Edit .env and run again.
        goto :end
    ) else (
        echo [ERROR] .env.example not found. Cannot create .env file.
        exit /b 1
    )
)

echo [INFO] Starting container...
docker-compose up -d
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Container started
    echo [INFO] View logs with: deploy.bat logs
) else (
    echo [ERROR] Failed to start container
    exit /b 1
)
goto :end

:stop
echo [INFO] Stopping container...
docker-compose stop
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Container stopped
)
goto :end

:restart
echo [INFO] Restarting container...
docker-compose restart
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Container restarted
)
goto :end

:logs
echo [INFO] Showing logs (Ctrl+C to exit)...
docker-compose logs -f rag
goto :end

:shell
echo [INFO] Accessing container shell...
docker-compose exec rag bash
goto :end

:index_data
echo [INFO] Indexing all data...

echo [INFO] 1/3: Parsing intent data...
docker-compose exec -T rag python scripts/indexing/parse_intent_data.py
if %ERRORLEVEL% neq 0 exit /b 1

echo [INFO] 2/3: Indexing intent data...
docker-compose exec -T rag python scripts/indexing/index_intent.py
if %ERRORLEVEL% neq 0 exit /b 1

echo [INFO] 3/3: Indexing product data...
docker-compose exec -T rag python scripts/indexing/index_products.py
if %ERRORLEVEL% neq 0 exit /b 1

echo [SUCCESS] All data indexed successfully
echo [INFO] To index FAQ data (requires ClickHouse):
echo   docker-compose exec rag python scripts/indexing/index_faq.py
goto :end

:status
echo [INFO] Container Status:
echo.

docker ps --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr /C:"rag-product-search" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Container is running
    echo.
    docker ps --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
) else (
    docker ps -a --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}" | findstr /C:"rag-product-search" >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo [WARNING] Container exists but is not running
        echo.
        docker ps -a --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}"
    ) else (
        echo [INFO] Container does not exist
    )
)
goto :end

:demo
echo [INFO] Running demo workflow...
docker-compose run --rm rag python scripts/demo/demo_full_workflow.py
goto :end

:test_stock
echo [INFO] Testing stock reader...
docker-compose run --rm rag python -m src.utils.stock_reader
goto :end

:clean
echo [WARNING] This will remove containers and images. Data volumes will be preserved.
set /p CONFIRM="Are you sure? (y/N): "
if /i "!CONFIRM!"=="y" (
    echo [INFO] Stopping and removing containers...
    docker-compose down

    echo [INFO] Removing image...
    docker rmi %IMAGE_NAME% 2>nul || echo [INFO] Image not found

    echo [SUCCESS] Cleanup complete
    echo [INFO] Data in database/ and data/ directories preserved
) else (
    echo [INFO] Cleanup cancelled
)
goto :end

:usage
echo RAG Product Search - Docker Deployment Helper (Windows)
echo.
echo Usage: deploy.bat ^<command^>
echo.
echo Commands:
echo   build       Build Docker image
echo   start       Start container (create if doesn't exist)
echo   stop        Stop container
echo   restart     Restart container
echo   logs        View container logs
echo   shell       Access container shell
echo   index       Index all data (intent, product)
echo   status      Check container status
echo   demo        Run demo workflow
echo   test        Test stock reader
echo   clean       Remove containers and images (preserves data)
echo   help        Show this help message
echo.
echo Examples:
echo   deploy.bat build
echo   deploy.bat start
echo   deploy.bat index
echo   deploy.bat logs
goto :end

:end
endlocal
