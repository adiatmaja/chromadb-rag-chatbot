"""
FAQ Data Indexing from CSV (Demo / No-ClickHouse mode).

Reads FAQ data from data/faq_data.csv and indexes it into ChromaDB.
Use this script when ClickHouse is not available (local demo, CI, portfolio showcase).
For production with ClickHouse use index_faq.py instead.

Usage:
    python scripts/indexing/index_faq_csv.py
"""

import sys
import os

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

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.config import VECTOR_DB_PATH, EMBEDDING_MODEL_NAME

FAQ_COLLECTION_NAME = "faq_collection"
FAQ_CSV_PATH = "data/faq_data.csv"

console = Console()


def load_faq_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {'id', 'question', 'answer', 'language'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"faq_data.csv is missing columns: {missing}")
    return df


def prepare_faq_data(df: pd.DataFrame):
    ids, documents, metadatas = [], [], []
    for _, row in df.iterrows():
        embedding_text = f"Pertanyaan: {row['question']} Jawaban: {row['answer']}"
        ids.append(f"faq_{row['id']}")
        documents.append(embedding_text)
        metadata = {
            'id': str(row['id']),
            'question': str(row['question']),
            'answer': str(row['answer']),
            'language': str(row['language']),
        }
        if 'created_at' in row and pd.notna(row['created_at']):
            metadata['created_at'] = str(row['created_at'])
        if 'updated_at' in row and pd.notna(row['updated_at']):
            metadata['updated_at'] = str(row['updated_at'])
        metadatas.append(metadata)
    return ids, documents, metadatas


def index_faq_csv():
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   FAQ Data Indexing (CSV → ChromaDB)   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    try:
        # Step 1: Load CSV
        console.print(f"\n[bold cyan]📥 Step 1: Loading FAQ data from {FAQ_CSV_PATH}...[/bold cyan]")
        df = load_faq_csv(FAQ_CSV_PATH)
        console.print(f"[green]✅ Loaded {len(df)} FAQ entries[/green]")

        sample_table = Table(show_header=True)
        sample_table.add_column("ID", width=5)
        sample_table.add_column("Question", width=55)
        for _, row in df.head(3).iterrows():
            q = str(row['question'])
            sample_table.add_row(str(row['id']), q[:52] + "..." if len(q) > 55 else q)
        console.print(sample_table)

        # Step 2: ChromaDB
        console.print(f"\n[bold cyan]💾 Step 2: Initializing ChromaDB...[/bold cyan]")
        Path(VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
        console.print("[green]✅ ChromaDB initialized[/green]")

        # Step 3: Embedding model
        console.print(f"\n[bold cyan]🤖 Step 3: Loading embedding model...[/bold cyan]")
        console.print(f"[cyan]Model: {EMBEDDING_MODEL_NAME}[/cyan]")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        console.print("[green]✅ Model loaded[/green]")

        # Step 4: Collection
        console.print(f"\n[bold cyan]📦 Step 4: Setting up collection...[/bold cyan]")
        try:
            client.delete_collection(name=FAQ_COLLECTION_NAME)
            console.print("[yellow]⚠️  Existing collection deleted[/yellow]")
        except Exception:
            pass
        collection = client.create_collection(
            name=FAQ_COLLECTION_NAME,
            metadata={"description": "FAQ embeddings from CSV", "hnsw:space": "cosine"}
        )
        console.print("[green]✅ Collection created[/green]")

        # Step 5: Prepare + embed + index
        ids, documents, metadatas = prepare_faq_data(df)

        console.print("\n[bold cyan]🔄 Step 5: Generating embeddings and indexing...[/bold cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing...", total=2)
            if "e5" in EMBEDDING_MODEL_NAME.lower():
                documents = [f"passage: {doc}" for doc in documents]
            embeddings = model.encode(documents, show_progress_bar=False)
            progress.update(task, advance=1)
            collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas
            )
            progress.update(task, advance=1)

        count = collection.count()
        console.print(f"\n[bold green]✅ Successfully indexed {count} FAQs![/bold green]")
        console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
        console.print("[bold green]✨ FAQ Indexing Completed Successfully! ✨[/bold green]")
        console.print("[bold green]" + "=" * 70 + "[/bold green]")
        console.print(f"\n[cyan]📊 Summary:[/cyan]")
        console.print(f"  • FAQs indexed: {count}")
        console.print(f"  • Source: {FAQ_CSV_PATH}")
        console.print(f"  • Collection: {FAQ_COLLECTION_NAME}")
        console.print(f"  • Database: {VECTOR_DB_PATH}")
        return 0

    except FileNotFoundError:
        console.print(f"\n[bold red]❌ File not found: {FAQ_CSV_PATH}[/bold red]")
        console.print("[yellow]Make sure data/faq_data.csv exists.[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[bold red]❌ Indexing failed: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(index_faq_csv())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Indexing cancelled by user[/yellow]")
        sys.exit(1)
