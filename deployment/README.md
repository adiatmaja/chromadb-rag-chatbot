# Deployment

This directory contains deployment scripts and Docker documentation for the RAG Product Search System.

## Files

- **deploy.sh**: Linux/macOS deployment helper script
- **deploy.bat**: Windows deployment helper script
- **verify_docker.bat**: Docker installation verification script
- **DOCKER.md**: Complete Docker documentation
- **DOCKER_TEST.md**: Docker testing guide

## Docker Files Location

The actual Docker files are in the project root for easy access:
- **../Dockerfile**: Docker image definition
- **../docker-compose.yml**: Docker Compose configuration

## Usage

All deployment scripts should be run from the **project root directory**.

### Linux/macOS

```bash
# From project root
./deployment/deploy.sh build
./deployment/deploy.sh start
./deployment/deploy.sh index
./deployment/deploy.sh logs
```

### Windows

```batch
# From project root
deployment\deploy.bat build
deployment\deploy.bat start
deployment\deploy.bat index
deployment\deploy.bat logs
```

### Direct Docker Commands

```bash
# From project root
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Documentation

- See **DOCKER.md** for complete Docker setup and usage guide
- See **DOCKER_TEST.md** for Docker testing procedures
- See main **../README.md** for general project documentation
