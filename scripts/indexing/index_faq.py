"""
FAQ Data Indexing Script.

Fetches FAQ data from ClickHouse and indexes it into ChromaDB vector database
for semantic search capabilities.

Usage:
    python index_faq.py
"""

import sys
import os

# Load onnxruntime mock for Docker compatibility (must be before chromadb)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from mock_onnxruntime import *
except ImportError:
    pass

import chromadb
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Fix Windows console encoding for Unicode characters
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Import configuration and utilities
from src.config import VECTOR_DB_PATH, EMBEDDING_MODEL_NAME
from src.utils.clickhouse_client import get_faq_data_from_clickhouse

# FAQ collection name (must match retriever.py)
FAQ_COLLECTION_NAME = "faq_collection"

console = Console()


def prepare_faq_data(df: pd.DataFrame):
    """
    Prepare FAQ data for embedding.

    Combines question and answer for better semantic search.

    Args:
        df: DataFrame with FAQ data

    Returns:
        tuple: (ids, documents, metadatas)
    """
    console.print("\n[bold cyan]📝 Preparing FAQ data...[/bold cyan]")

    ids = []
    documents = []
    metadatas = []

    for _, row in df.iterrows():
        # Create embedding text from question + answer
        embedding_text = f"Question: {row['question']} Answer: {row['answer']}"

        ids.append(f"faq_{row['id']}")
        documents.append(embedding_text)

        metadata = {
            'id': str(row['id']),
            'question': str(row['question']),
            'answer': str(row['answer']),
            'language': str(row['language']),
        }

        if pd.notna(row.get('created_at')):
            metadata['created_at'] = str(row['created_at'])
        if pd.notna(row.get('updated_at')):
            metadata['updated_at'] = str(row['updated_at'])

        metadatas.append(metadata)

    console.print(f"[green]✅ Prepared {len(ids)} FAQ records[/green]")

    return ids, documents, metadatas


def index_faq_data():
    """
    Main indexing function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   FAQ Data Indexing (ClickHouse → ChromaDB)   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    try:
        # Step 1: Fetch data from ClickHouse
        console.print("\n[bold cyan]📥 Step 1: Fetching FAQ data from ClickHouse...[/bold cyan]")
        df = get_faq_data_from_clickhouse()

        if len(df) == 0:
            console.print("[yellow]⚠️  No FAQ data found[/yellow]")
            return 1

        # Show sample
        console.print("\n[dim]Sample FAQ entries:[/dim]")
        sample_table = Table(show_header=True)
        sample_table.add_column("ID", width=5)
        sample_table.add_column("Question", width=50)

        for _, row in df.head(3).iterrows():
            question = str(row['question'])[:47] + "..." if len(str(row['question'])) > 50 else str(row['question'])
            sample_table.add_row(str(row['id']), question)

        console.print(sample_table)

        # Step 2: Initialize ChromaDB
        console.print(f"\n[bold cyan]💾 Step 2: Initializing ChromaDB...[/bold cyan]")
        Path(VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
        console.print("[green]✅ ChromaDB initialized[/green]")

        # Step 3: Load embedding model
        console.print(f"\n[bold cyan]🤖 Step 3: Loading embedding model...[/bold cyan]")
        console.print(f"[cyan]Model: {EMBEDDING_MODEL_NAME}[/cyan]")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        console.print("[green]✅ Model loaded[/green]")

        # Step 4: Create/reset collection
        console.print(f"\n[bold cyan]📦 Step 4: Setting up collection...[/bold cyan]")
        try:
            client.delete_collection(name=FAQ_COLLECTION_NAME)
            console.print("[yellow]⚠️  Existing collection deleted[/yellow]")
        except:
            pass

        collection = client.create_collection(
            name=FAQ_COLLECTION_NAME,
            metadata={"description": "FAQ embeddings from ClickHouse", "hnsw:space": "cosine"}
        )
        console.print("[green]✅ Collection created[/green]")

        # Step 5: Prepare data
        ids, documents, metadatas = prepare_faq_data(df)

        # Step 6: Generate embeddings and index
        console.print("\n[bold cyan]🔄 Step 5: Generating embeddings and indexing...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing...", total=2)

            # Generate embeddings
            embeddings = model.encode(documents, show_progress_bar=False)
            progress.update(task, advance=1)

            # Add to ChromaDB
            collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas
            )
            progress.update(task, advance=1)

        # Step 7: Verify
        count = collection.count()
        console.print(f"\n[bold green]✅ Successfully indexed {count} FAQs![/bold green]")

        # Success message
        console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
        console.print("[bold green]✨ FAQ Indexing Completed Successfully! ✨[/bold green]")
        console.print("[bold green]" + "=" * 70 + "[/bold green]")

        console.print("\n[cyan]📊 Summary:[/cyan]")
        console.print(f"  • FAQs indexed: {count}")
        console.print(f"  • Collection: {FAQ_COLLECTION_NAME}")
        console.print(f"  • Database: {VECTOR_DB_PATH}")

        return 0

    except ValueError as e:
        console.print(f"\n[bold red]❌ Configuration Error: {e}[/bold red]")
        console.print("\n[yellow]💡 Action Required:[/yellow]")
        console.print("  Configure ClickHouse credentials in .env file:")
        console.print("  - CLICKHOUSE_HOST")
        console.print("  - CLICKHOUSE_PORT")
        console.print("  - CLICKHOUSE_DB_NAME")
        return 1

    except Exception as e:
        console.print(f"\n[bold red]❌ Indexing failed: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    try:
        exit_code = index_faq_data()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Indexing cancelled by user[/yellow]")
        sys.exit(1)
