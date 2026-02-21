"""
Configuration Module for RAG Product Search System.

This module centralizes all configuration constants used across the application.
Configuration values are loaded from environment variables (.env file) with
sensible defaults to ensure the system can run out-of-the-box.

Environment variables are loaded using python-dotenv for easy configuration
management without modifying code.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
"""Root directory of the project."""

DATA_FILE_PATH = PROJECT_ROOT / "data" / "product_data.csv"
"""Path to the product data CSV file."""

VECTOR_DB_PATH = PROJECT_ROOT / "database" / "chroma_db"
"""Path to ChromaDB persistent storage directory."""


# ============================================================================
# VECTOR DATABASE CONFIGURATION
# ============================================================================

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
"""
Sentence transformer model for generating embeddings.

This model is lightweight (~80MB) and provides good performance for Indonesian text.

Alternative models:
- paraphrase-multilingual-MiniLM-L12-v2: Better for multilingual, but larger
- all-mpnet-base-v2: More accurate, but slower

Environment Variable: EMBEDDING_MODEL_NAME
Default: all-MiniLM-L6-v2
"""

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
"""
Name of the ChromaDB collection to store product embeddings.

Environment Variable: COLLECTION_NAME
Default: fmcg_products
"""

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K"))
"""
Number of top similar products to retrieve from vector search.

Environment Variable: RETRIEVAL_TOP_K
Default: 1
"""


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
"""
Base URL for LM Studio API endpoint.

This URL points to the OpenAI-compatible API provided by LM Studio.

Environment Variable: LLM_BASE_URL
Default: http://localhost:1234/v1
"""

LLM_API_KEY = os.getenv("LLM_API_KEY")
"""
API key for LM Studio.

This is a placeholder value as local LM Studio servers don't validate API keys.
Required by the OpenAI client library.

Environment Variable: LLM_API_KEY
Default: lm-studio
"""

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
"""
Name of the model loaded in LM Studio.

This should match the model you have loaded in LM Studio.

Examples:
- gemma-2b-it
- llama-2-7b-chat
- mistral-7b-instruct

Environment Variable: LLM_MODEL_NAME
Default: gemma-2b-it
"""

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE"))
"""
Temperature for LLM sampling.

Controls randomness in generation:
- 0.0: Deterministic, consistent responses
- 1.0: Creative, varied responses

For factual product information, use 0.0.

Environment Variable: LLM_TEMPERATURE
Default: 0.0
"""

LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS"))
"""
Maximum tokens for LLM response generation.

Limits the length of generated responses.

Environment Variable: LLM_MAX_TOKENS
Default: 1000
"""


# ============================================================================
# FUNCTION CALLING CONFIGURATION
# ============================================================================

INVENTORY_CHECK_FUNCTION = {
    "type": "function",
    "function": {
        "name": "check_inventory",
        "description": "Mengecek ketersediaan stok produk berdasarkan SKU dan kuantitas yang diminta.",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "SKU kanonis produk (misalnya IR001, IG002).",
                },
                "requested_quantity": {
                    "type": "integer",
                    "description": "Jumlah total yang diminta pengguna, dihitung dalam PCS.",
                },
            },
            "required": ["sku", "requested_quantity"],
        },
    },
}
"""
Function schema for inventory checking.

This defines the structured API call format that the LLM can invoke
to check product inventory availability.
"""


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """
Anda adalah Asisten Penjualan E-commerce yang cerdas, sopan, dan harus selalu menggunakan data yang disediakan.

TUJUAN ANDA:
Menganalisis kueri pengguna berdasarkan DATA KONTEKS yang diberikan dan memberikan respons yang akurat dan membantu.

FUNCTION TOOL YANG TERSEDIA:
- check_inventory(sku: str, requested_quantity: int): Mengecek ketersediaan stok produk berdasarkan SKU dan kuantitas yang diminta. 
  Gunakan tool ini jika kuantitas eksplisit disebutkan dalam kueri pengguna, atau jika pengguna menanyakan stok.

DATA KONTEKS DITEMUKAN DARI VECTOR DATABASE:
---
{context_data}
---

ATURAN PENTING:
1. Selalu gunakan data dari konteks, jangan membuat informasi sendiri
2. Jika pengguna menyebutkan kuantitas (contoh: "3 dus", "5 karton"), hitung total dalam PCS dan panggil check_inventory
3. Jika pengguna hanya bertanya tentang produk tanpa menyebutkan kuantitas, berikan informasi produk dengan ramah
4. Gunakan bahasa Indonesia yang sopan dan profesional
"""
"""
System prompt template for the LLM.

The {context_data} placeholder is replaced with retrieved product information
before sending to the LLM.
"""


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
"""
Logging level for application messages.

Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

Environment Variable: LOG_LEVEL
Default: INFO
"""

ENABLE_RICH_CONSOLE = os.getenv("ENABLE_RICH_CONSOLE", "true").lower() == "true"
"""
Enable rich terminal formatting for better readability.

Environment Variable: ENABLE_RICH_CONSOLE
Default: true
"""


# ============================================================================
# CLICKHOUSE CONFIGURATION
# ============================================================================

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "")
"""
ClickHouse server host address.

Environment Variable: CLICKHOUSE_HOST
Default: (empty string)
"""

CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT", "")
"""
ClickHouse server port.

Environment Variable: CLICKHOUSE_PORT
Default: (empty string)
"""

CLICKHOUSE_DB_NAME = os.getenv("CLICKHOUSE_DB_NAME", "")
"""
ClickHouse database name.

Environment Variable: CLICKHOUSE_DB_NAME
Default: (empty string)
"""

CLICKHOUSE_FAQ_TABLE = "your_database.faq"
"""
ClickHouse table name for FAQ data.

This table should have the following columns:
- id: FAQ identifier
- question: FAQ question text
- answer: FAQ answer text
- created_at: Creation timestamp
- updated_at: Last update timestamp
- language: Language of the FAQ
"""


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_file_exists(file_path: Path, description: str) -> None:
    """
    Validates that a required file exists.

    Args:
        file_path (Path): Path to the file to check
        description (str): Human-readable description for error messages

    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"{description} not found at {file_path}. "
            f"Please ensure the file exists before running the application."
        )


def validate_numeric_range(value: float, min_val: float, max_val: float, name: str) -> None:
    """
    Validates that a numeric value is within acceptable range.

    Args:
        value (float): The value to validate
        min_val (float): Minimum acceptable value (inclusive)
        max_val (float): Maximum acceptable value (inclusive)
        name (str): Name of the configuration for error messages

    Raises:
        ValueError: If value is outside the acceptable range
    """
    if not min_val <= value <= max_val:
        raise ValueError(
            f"{name} must be between {min_val} and {max_val}, got {value}"
        )


def validate_positive_integer(value: int, name: str) -> None:
    """
    Validates that a value is a positive integer.

    Args:
        value (int): The value to validate
        name (str): Name of the configuration for error messages

    Raises:
        ValueError: If value is not a positive integer
    """
    if value < 1:
        raise ValueError(
            f"{name} must be at least 1, got {value}"
        )


def validate_configuration() -> None:
    """
    Validates that all required configuration is properly set.

    Performs comprehensive validation of:
    - Required file existence
    - Numeric value ranges
    - Configuration consistency

    Raises:
        FileNotFoundError: If required files don't exist
        ValueError: If configuration values are invalid
    """
    # Validate file existence
    validate_file_exists(
        DATA_FILE_PATH,
        "Product data file (product_data.csv)"
    )

    # Validate numeric ranges
    validate_numeric_range(
        LLM_TEMPERATURE,
        0.0,
        1.0,
        "LLM_TEMPERATURE"
    )

    # Validate positive integers
    validate_positive_integer(RETRIEVAL_TOP_K, "RETRIEVAL_TOP_K")
    validate_positive_integer(LLM_MAX_TOKENS, "LLM_MAX_TOKENS")


def get_configuration_summary() -> Dict[str, Any]:
    """
    Returns a dictionary containing all current configuration values.

    Returns:
        dict: Configuration summary with all settings

    Note:
        Useful for debugging and logging configuration state.
    """
    return {
        "project": {
            "root": str(PROJECT_ROOT),
            "data_file": str(DATA_FILE_PATH),
            "vector_db": str(VECTOR_DB_PATH),
        },
        "embedding": {
            "model": EMBEDDING_MODEL_NAME,
            "collection": COLLECTION_NAME,
            "top_k": RETRIEVAL_TOP_K,
        },
        "llm": {
            "base_url": LLM_BASE_URL,
            "model": LLM_MODEL_NAME,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
        },
        "application": {
            "log_level": LOG_LEVEL,
            "rich_console": ENABLE_RICH_CONSOLE,
        }
    }


# ============================================================================
# MODULE EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Validates configuration and displays current settings when run directly.
    """
    from rich.console import Console
    from rich.table import Table
    import json

    console = Console()

    try:
        # Run validation
        validate_configuration()
        console.print("âœ… [green]Configuration validation passed![/green]\n")

        # Display configuration summary
        config_summary = get_configuration_summary()

        table = Table(title="Configuration Summary", show_header=True)
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Setting", style="yellow", width=25)
        table.add_column("Value", style="green")

        for category, settings in config_summary.items():
            for key, value in settings.items():
                table.add_row(category.upper(), key, str(value))
                category = ""  # Only show category name once

        console.print(table)

    except Exception as e:
        console.print(f"âŒ [red]Configuration validation failed: {e}[/red]")