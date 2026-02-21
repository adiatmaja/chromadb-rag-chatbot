# RAG Product Search System - Setup Guide

## 🎯 Quick Start (5 Minutes)

Follow these steps to get the system running quickly:

### 1. Clone and Navigate

```bash
git clone <your-repository-url>
cd fmcg_rag_poc
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings (optional for defaults)
nano .env
```

### 5. Run Automated Setup

```bash
python setup.py
```

That's it! The setup script will guide you through the rest.

---

## 📝 Detailed Setup Instructions

### Step 1: Prerequisites Check

#### Python Version

Verify you have Python 3.9 or higher:

```bash
python --version
# Should show: Python 3.9.x or higher
```

#### System Resources

- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space
- **OS**: Windows, macOS, or Linux

### Step 2: Install LM Studio (Optional)

LM Studio is only required for the full RAG pipeline with natural language generation. The retrieval system works without it.

1. **Download**: Visit [https://lmstudio.ai/](https://lmstudio.ai/)
2. **Install**: Follow platform-specific instructions
3. **Download a Model**:
   - Open LM Studio
   - Browse models (search for "gemma-2b-it" or "llama-2-7b")
   - Download your chosen model
4. **Start Server**:
   - Load the model
   - Click "Start Server"
   - Default endpoint: `http://localhost:1234`

### Step 3: Project Setup

#### Create Project Directory

```bash
mkdir fmcg_rag_poc
cd fmcg_rag_poc
```

#### Initialize Git (Optional)

```bash
git init
```

#### Add Project Files

Ensure you have these files:
- `config.py`
- `index_data.py`
- `search_agent.py`
- `llm_processor.py`
- `setup.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `product_data.csv`

### Step 4: Virtual Environment Setup

#### Why Use Virtual Environment?

- Isolates project dependencies
- Prevents conflicts with system packages
- Makes deployment easier
- Enables exact dependency reproduction

#### Create Virtual Environment

```bash
# Using venv (built-in)
python -m venv venv

# Or using virtualenv
virtualenv venv
```

#### Activate Virtual Environment

```bash
# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### Verify Activation

```bash
which python
# Should point to venv/bin/python
```

### Step 5: Install Dependencies

#### Install All Requirements

```bash
pip install -r requirements.txt
```

#### Verify Installation

```bash
pip list
```

You should see:
- pandas
- chromadb
- sentence-transformers
- torch
- openai
- rich
- python-dotenv
- requests

#### Troubleshooting Installation

**Issue: pip is not found**
```bash
python -m pip install --upgrade pip
```

**Issue: torch installation fails**
```bash
# Install CPU-only version (lighter)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Issue: ChromaDB installation fails**
```bash
# Install build dependencies first
pip install --upgrade setuptools wheel
pip install chromadb
```

### Step 6: Configure Environment Variables

#### Understanding .env Files

The `.env` file stores configuration without hardcoding values in code. This allows:
- Easy deployment across environments
- Secure secret management
- Configuration without code changes
- Team-specific settings

#### Create Your .env File

```bash
# Copy the example
cp .env.example .env
```

#### Edit Configuration

Open `.env` in your text editor:

```bash
# Using nano
nano .env

# Using vim
vim .env

# Using VS Code
code .env
```

#### Configuration Options

##### Basic Configuration (Recommended)

For most users, the defaults work fine:

```env
# .env file (minimal configuration)
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=gemma-2b-it
```

##### Advanced Configuration

Customize for your specific needs:

```env
# LLM Settings
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL_NAME=llama-2-7b-chat  # Your loaded model
LLM_TEMPERATURE=0.1             # Slightly more creative
LLM_MAX_TOKENS=1500             # Longer responses

# Vector Database
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2  # Better multilingual
COLLECTION_NAME=my_products
RETRIEVAL_TOP_K=3  # Return top 3 results

# Application
LOG_LEVEL=DEBUG  # More verbose logging
ENABLE_RICH_CONSOLE=true
```

##### Production Configuration

For deployment:

```env
# Use environment-specific URLs
LLM_BASE_URL=https://your-llm-service.com/v1
LLM_API_KEY=your-secure-api-key

# Optimize for production
LLM_TEMPERATURE=0.0
LOG_LEVEL=WARNING
RETRIEVAL_TOP_K=1
```

#### Validate Configuration

```bash
python config.py
```

This will:
- Load environment variables
- Validate all settings
- Display configuration summary
- Report any errors

### Step 7: Prepare Product Data

#### Create product_data.csv

Your CSV must have these columns:

```csv
sku,official_name,colloquial_names,pack_size_desc,embedding_text
```

#### Example Data

```csv
sku,official_name,colloquial_names,pack_size_desc,embedding_text
IR001,Indomie Mi Instan Rasa Kaldu Ayam,"Indomie Rebus; Indomie Kuning; Mie Soto Ayam",1 dus = 40 pcs,"Produk Indomie Mi Instan Rasa Kaldu Ayam, juga dikenal sebagai Indomie Rebus, Indomie Kuning, Mie Soto Ayam. SKU IR001. Kemasan 1 dus berisi 40 bungkus."
IG002,Indomie Mi Instan Goreng Original,"Indomie Goreng; Mi Goreng Bungkusan Merah",1 dus = 40 pcs,"Produk Indomie Mi Instan Goreng Original. Nama lain yang populer adalah Indomie Goreng atau Mi Goreng Bungkusan Merah. SKU IG002. Kemasan 1 dus berisi 40 bungkus."
```

#### Data Quality Tips

1. **Rich embedding_text**: Include all relevant information
2. **Multiple colloquial names**: Separate with semicolons
3. **Clear pack sizes**: Use readable formats
4. **Unique SKUs**: Ensure no duplicates

### Step 8: Run Automated Setup

The setup script automates the remaining steps:

```bash
python setup.py
```

#### What the Setup Script Does

1. ✅ Checks Python version
2. ✅ Verifies all required files exist
3. ✅ Installs/updates dependencies
4. ✅ Validates configuration
5. ✅ Builds vector database
6. ✅ Tests retrieval system
7. ✅ Checks LM Studio connection
8. ✅ Generates setup report

#### Expected Output

```
════════════════════════════════════════════════════════════════════
   RAG Product Search System - Setup Wizard   
════════════════════════════════════════════════════════════════════

🔍 Checking Python version...
✅ Python 3.9.x detected

📦 Installing dependencies...
✅ Dependencies installed successfully

⚙️ Validating configuration...
✅ Configuration validated

🗂️ Building vector database...
✅ Indexed 10 products

🧪 Testing retrieval system...
✅ Retrieval test passed

🤖 Checking LM Studio connection...
✅ LM Studio is running and accessible

════════════════════════════════════════════════════════════════════
              Setup Report              
════════════════════════════════════════════════════════════════════

✨ Setup completed successfully!

Next Steps:
  1. Test retrieval: python search_agent.py
  2. Test full RAG: python llm_processor.py
```

### Step 9: Manual Steps (Alternative to Automated Setup)

If you prefer manual setup or the automated script fails:

#### Build Vector Database

```bash
python index_data.py
```

This will:
- Load product data from CSV
- Generate embeddings
- Store in ChromaDB
- Create `chroma_db/` directory

#### Test Retrieval

```bash
python search_agent.py
```

This will:
- Run test queries
- Display product matches
- Show similarity scores

#### Test Full RAG Pipeline

```bash
python llm_processor.py
```

This will:
- Test complete RAG system
- Demonstrate function calling
- Generate natural language responses

### Step 10: Verify Installation

#### Quick Test

```python
python -c "from search_agent import ProductRetriever; r = ProductRetriever(); print('✅ Installation successful!')"
```

#### Full System Check

```bash
# Test configuration
python config.py

# Test retrieval
python search_agent.py

# Test LLM (requires LM Studio)
python llm_processor.py
```

---

## 🔧 Configuration Management

### Environment Variables Priority

Configuration is loaded in this order (later overrides earlier):

1. **Default values** in `config.py`
2. **Environment variables** from OS
3. **.env file** in project root

### Multiple Environments

#### Development

```bash
# .env.development
LLM_BASE_URL=http://localhost:1234/v1
LOG_LEVEL=DEBUG
```

#### Production

```bash
# .env.production
LLM_BASE_URL=https://api.example.com/v1
LOG_LEVEL=WARNING
```

Load specific environment:

```bash
# Development
cp .env.development .env
python llm_processor.py

# Production
cp .env.production .env
python llm_processor.py
```

### Secrets Management

**Never commit sensitive data!**

The `.gitignore` file prevents committing:
- `.env`
- `.env.local`
- `.env.production`

Keep `.env.example` for documentation:
- Contains all required variables
- Uses placeholder values
- Safe to commit

---

## 🚀 Deployment

### Local Development

```bash
# Use default settings
python search_agent.py
```

### Server Deployment

1. **Set environment variables** on server:
```bash
export LLM_BASE_URL=https://your-server/v1
export LLM_API_KEY=your-secure-key
```

2. **Run without .env file** (uses OS environment):
```bash
python llm_processor.py
```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Environment variables passed at runtime
CMD ["python", "llm_processor.py"]
```

Run with environment:
```bash
docker run -e LLM_BASE_URL=http://host:1234/v1 your-image
```

---

## ❓ Troubleshooting

### Common Issues

#### .env file not loading

**Symptoms**: Using default values even after editing .env

**Solutions**:
1. Verify file is named `.env` (not `.env.txt`)
2. Check file is in project root
3. Restart Python interpreter
4. Verify python-dotenv is installed:
   ```bash
   pip install python-dotenv
   ```

#### Configuration validation fails

**Symptoms**: Error messages from `config.py`

**Solutions**:
1. Check required files exist:
   ```bash
   ls product_data.csv
   ```
2. Validate .env syntax (no spaces around `=`)
3. Ensure numeric values are valid
4. Run diagnostics:
   ```bash
   python config.py
   ```

#### LM Studio not connecting

**Symptoms**: Connection refused errors

**Solutions**:
1. Start LM Studio server
2. Verify URL in .env: `LLM_BASE_URL=http://localhost:1234/v1`
3. Test connection:
   ```bash
   curl http://localhost:1234/v1/models
   ```
4. Check firewall settings

#### ChromaDB errors

**Symptoms**: Collection not found, database errors

**Solutions**:
1. Delete and rebuild:
   ```bash
   rm -rf chroma_db/
   python index_data.py
   ```
2. Check permissions on `chroma_db/` directory
3. Verify disk space available

---

## 📚 Next Steps

After successful setup:

1. **Customize Product Data**: Add your products to `product_data.csv`
2. **Test Queries**: Try different search patterns
3. **Adjust Configuration**: Fine-tune settings in `.env`
4. **Integrate**: Connect to your existing systems
5. **Monitor**: Check logs and performance

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide thoroughly
2. Run diagnostics: `python setup.py`
3. Validate config: `python config.py`
4. Review error messages carefully
5. Check system requirements

---

**Setup complete! You're ready to build intelligent product search. 🎉**