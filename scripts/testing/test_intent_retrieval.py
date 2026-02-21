"""
Intent Classification Demo

Demonstrates the intent classification system using the UnifiedRetriever
with intent collection.

Usage:
    python test_intent_retrieval.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.retriever import UnifiedRetriever, ContentType
from rich.console import Console
from rich.panel import Panel

console = Console()


def test_intent_classification():
    """
    Tests intent classification with various Indonesian customer queries.
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]    Intent Classification System - Test Demo    [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    # Initialize retriever
    try:
        console.print("\n[cyan]Initializing retriever...[/cyan]")
        retriever = UnifiedRetriever()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize retriever: {e}[/bold red]")
        console.print("\n[yellow]💡 Make sure to run: python index_intent.py[/yellow]")
        return 1

    # Test queries covering different intents
    test_queries = [
        # Cart operations
        "Saya ingin pesan 2 buah indomie",
        "Tambahkan ke keranjang",
        "Tidak jadi pesan",
        "Kurangi 1",

        # Promo codes
        "ABC123DE",
        "Tidak pakai promo",

        # Account questions
        "Saya pelanggan prioritas bukan?",
        "Berapa poin saya?",

        # Product inquiries
        "Ada indomie tidak?",
        "Mau lihat katalog produk",

        # Greetings and farewells
        "Halo kak",
        "Selamat pagi",
        "Terima kasih ya",

        # Favorite product check
        "Saya mau cek produk favorit",
        "Mie Instan",
        "Lanjut",

        # Checkout
        "Checkout sekarang",
        "Saya mau bayar",

        # General questions
        "Bagaimana cara pesan?",
        "Ongkir ke daerah saya berapa?",
    ]

    console.print(f"\n[bold cyan]Testing {len(test_queries)} queries...[/bold cyan]\n")

    # Test each query (search only intents)
    for i, query in enumerate(test_queries, 1):
        console.print(f"\n[bold yellow]Query {i}/{len(test_queries)}:[/bold yellow]")
        console.print(Panel(query, style="yellow", border_style="dim"))

        # Search only in intent collection
        result = retriever.search(
            query=query,
            search_products=False,
            search_faqs=False,
            search_intents=True,
            top_k=1
        )

        if result and result.content_type == ContentType.INTENT:
            intent_name = result.metadata.get('intent_name', 'unknown')
            console.print(f"[bold green]✓ Detected Intent:[/bold green] [cyan]{intent_name}[/cyan]")
            console.print(f"[dim]Confidence: {result.relevance_score:.2%}[/dim]")
        else:
            console.print("[bold red]✗ No intent detected[/bold red]")

        # Add separator
        if i < len(test_queries):
            console.print("[dim]" + "-" * 70 + "[/dim]")

    console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
    console.print("[bold green]✨ Intent Classification Test Completed! ✨[/bold green]")
    console.print("[bold green]" + "=" * 70 + "[/bold green]")

    return 0


def test_combined_search():
    """
    Tests combined search across products, FAQs, and intents.
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]    Combined Search Test (Products + FAQs + Intents)    [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    try:
        retriever = UnifiedRetriever()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize retriever: {e}[/bold red]")
        return 1

    # Test queries that could match multiple types
    test_queries = [
        "indomie goreng",  # Should match product
        "bagaimana cara pesan?",  # Should match FAQ or intent
        "Checkout",  # Should match intent
        "ada aqua tidak?",  # Could match product or intent
    ]

    for query in test_queries:
        console.print(f"\n[bold yellow]Query:[/bold yellow] {query}")
        result = retriever.search(
            query=query,
            search_products=True,
            search_faqs=True,
            search_intents=True
        )

        if result:
            console.print(f"[bold green]Best Match Type:[/bold green] {result.content_type.value.upper()}")
        else:
            console.print("[red]No match found[/red]")

        console.print("[dim]" + "-" * 70 + "[/dim]")

    return 0


if __name__ == "__main__":
    try:
        # Run intent classification test
        exit_code = test_intent_classification()

        # Run combined search test
        if exit_code == 0:
            console.print("\n\n")
            exit_code = test_combined_search()

        sys.exit(exit_code)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Test cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Test failed: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)
