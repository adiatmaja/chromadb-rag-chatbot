@echo off
REM Interactive Docker Workflow Runner for Windows
REM This script runs the RAG system in interactive mode

echo ========================================
echo  Starting RAG Interactive Query System
echo ========================================
echo.

REM Start the container
echo Starting Docker container...
docker-compose up

pause
