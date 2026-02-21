"""
Intent Data Indexing Script.

Loads intent data from CSV and indexes it into ChromaDB vector database
for semantic search and intent classification.

Usage:
    python index_intent.py
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

# Import configuration
from src.config import VECTOR_DB_PATH, EMBEDDING_MODEL_NAME

# Intent collection name (must match retriever.py)
INTENT_COLLECTION_NAME = "intent_collection"
INTENT_DATA_PATH = "data/intent_data.csv"

console = Console()


def load_intent_data():
    """
    Load intent data from CSV file.

    Returns:
        pd.DataFrame: Intent data
    """
    console.print(f"\n[bold cyan]📂 Loading intent data from {INTENT_DATA_PATH}...[/bold cyan]")

    if not Path(INTENT_DATA_PATH).exists():
        raise FileNotFoundError(
            f"Intent data file not found: {INTENT_DATA_PATH}\n"
            f"Please run: python parse_intent_data.py"
        )

    df = pd.read_csv(INTENT_DATA_PATH, encoding='utf-8')
    console.print(f"[green]✅ Loaded {len(df)} intent definitions[/green]")

    return df


def prepare_intent_data(df: pd.DataFrame):
    """
    Prepare intent data for embedding.

    Uses the pre-computed embedding_text column which combines:
    - Intent name (canonical query)
    - Description
    - Query variation examples

    Args:
        df: DataFrame with intent data

    Returns:
        tuple: (ids, documents, metadatas)
    """
    console.print("\n[bold cyan]📝 Preparing intent data...[/bold cyan]")

    ids = []
    documents = []
    metadatas = []

    for _, row in df.iterrows():
        intent_name = row['intent_name']

        # Use the pre-computed embedding_text
        embedding_text = row['embedding_text']

        ids.append(f"intent_{intent_name}")
        documents.append(embedding_text)

        # Store metadata for retrieval
        metadata = {
            'intent_name': intent_name,
            'description': str(row['description']),
            'example_count': int(row['example_count'])
        }

        # Store query variations if available
        if pd.notna(row.get('query_variations')) and row['query_variations']:
            metadata['query_variations'] = str(row['query_variations'])

        metadatas.append(metadata)

    console.print(f"[green]✅ Prepared {len(ids)} intent records[/green]")

    return ids, documents, metadatas


def index_intent_data():
    """
    Main indexing function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   Intent Data Indexing (CSV → ChromaDB)   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    try:
        # Step 1: Load data from CSV
        df = load_intent_data()

        # Show sample
        console.print("\n[dim]Sample intent entries:[/dim]")
        sample_table = Table(show_header=True)
        sample_table.add_column("Intent Name", width=35)
        sample_table.add_column("Examples", width=8, justify="center")
        sample_table.add_column("Description", width=45)

        for _, row in df.head(5).iterrows():
            intent_name = str(row['intent_name'])
            example_count = str(row['example_count'])
            description = str(row['description'])[:42] + "..." if len(str(row['description'])) > 45 else str(row['description'])
            sample_table.add_row(intent_name, example_count, description)

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
            client.delete_collection(name=INTENT_COLLECTION_NAME)
            console.print("[yellow]⚠️  Existing collection deleted[/yellow]")
        except:
            pass

        collection = client.create_collection(
            name=INTENT_COLLECTION_NAME,
            metadata={"description": "Intent embeddings for intent classification", "hnsw:space": "cosine"}
        )
        console.print("[green]✅ Collection created[/green]")

        # Step 5: Prepare data
        ids, documents, metadatas = prepare_intent_data(df)

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
        console.print(f"\n[bold green]✅ Successfully indexed {count} intents![/bold green]")

        # Success message
        console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
        console.print("[bold green]✨ Intent Indexing Completed Successfully! ✨[/bold green]")
        console.print("[bold green]" + "=" * 70 + "[/bold green]")

        console.print("\n[cyan]📊 Summary:[/cyan]")
        console.print(f"  • Intents indexed: {count}")
        console.print(f"  • Collection: {INTENT_COLLECTION_NAME}")
        console.print(f"  • Database: {VECTOR_DB_PATH}")
        console.print(f"  • Total examples: {df['example_count'].sum()}")

        return 0

    except FileNotFoundError as e:
        console.print(f"\n[bold red]❌ File Error: {e}[/bold red]")
        return 1

    except Exception as e:
        console.print(f"\n[bold red]❌ Indexing failed: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    try:
        exit_code = index_intent_data()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Indexing cancelled by user[/yellow]")
        sys.exit(1)
