# Documentation Index

This directory contains all documentation for the RAG Product Search System.

## 📚 Quick Navigation

### Getting Started
- [Quick Start Guide](QUICK_START.md) - Get up and running in 5 minutes
- [Intent Classification System](INTENT_SYSTEM.md) - Understanding intent detection

### Setup Guides
- [Setup Complete](setup/INDEXING_COMPLETE.md) - First-time indexing completion summary

### Docker Documentation
- [Docker Quick Start](docker/DOCKER_USAGE.md) - How to use Docker workflow
- [Docker Setup Guide](../deployment/DOCKER.md) - Complete Docker deployment
- [Docker Fixes](docker/FINAL_DOCKER_FIX.md) - Technical details on Docker fixes
- [Docker Issues](docker/DOCKER_FIXES_SUMMARY.md) - Summary of resolved issues

### Deployment
- See [deployment/](../deployment/) directory for deployment scripts and guides

### Main Documentation
- [README](../README.md) - Main project documentation
- [CLAUDE.md](../CLAUDE.md) - Instructions for Claude Code
- [CHANGELOG](CHANGELOG.md) - Version history

## 📁 Directory Structure

```
docs/
├── README.md                    # This file
├── QUICK_START.md              # Quick start guide
├── INTENT_SYSTEM.md            # Intent classification docs
├── setup/                      # Setup guides
│   └── INDEXING_COMPLETE.md   # First-time setup summary
└── docker/                     # Docker-specific docs
    ├── DOCKER_USAGE.md        # Docker usage guide
    ├── FINAL_DOCKER_FIX.md   # Docker technical fixes
    └── DOCKER_FIXES_SUMMARY.md # Fix summary
```

## 🔧 Windows Scripts

All Windows batch scripts are now in `scripts/windows/`:
- `docker-setup-index.bat` - Automated indexing setup
- `docker-run-interactive.bat` - Quick start interactive mode
- `docker-rebuild.bat` - Rebuild Docker container

## 🚀 Common Tasks

### First-Time Setup
```bash
# Windows
scripts\windows\docker-setup-index.bat

# Linux/Mac
bash deployment/deploy.sh
```

### Run Interactive System
```bash
# Windows
scripts\windows\docker-run-interactive.bat

# Linux/Mac
docker-compose up
```

### View Logs
```bash
docker logs rag-product-search -f
```

## 📖 Additional Resources

- **Examples**: See [examples/](../examples/) for integration examples
- **Tests**: See [tests/](../tests/) for test suites
- **Scripts**: See [scripts/](../scripts/) for utility scripts
- **Data**: See [data/](../data/) for data files

## 🆘 Need Help?

1. Check [README.md](../README.md) for general information
2. Check [DOCKER_USAGE.md](docker/DOCKER_USAGE.md) for Docker-specific help
3. Check [deployment/DOCKER.md](../deployment/DOCKER.md) for deployment guides
4. Check issue tracker at project repository
