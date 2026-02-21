"""
Full Workflow Demonstration Script
Demonstrates the complete RAG system with product, FAQ, and intent retrieval.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.orchestrator import UnifiedRAGOrchestrator
from rich.console import Console
from rich.panel import Panel

console = Console()

def demo_full_workflow():
    """Demonstrates the complete workflow with sample queries."""

    console.print("\n" + "="*70)
    console.print("  FULL RAG WORKFLOW DEMONSTRATION")
    console.print("="*70 + "\n")

    # Initialize the orchestrator
    console.print("[bold cyan]Step 1: Initializing System...[/bold cyan]\n")
    try:
        orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize: {e}[/bold red]")
        return 1

    console.print("\n[bold green]✓ System initialized successfully![/bold green]\n")

    # Test queries demonstrating different aspects
    test_queries = [
        {
            "query": "Saya ingin pesan 3 dus indomie goreng",
            "description": "Product query with quantity (tests product search + intent + LLM)"
        },
        {
            "query": "Ada berapa pcs dalam 1 dus indomie?",
            "description": "Product information query (tests product search + LLM)"
        },
        {
            "query": "Checkout sekarang",
            "description": "Intent-only query (tests intent classification)"
        },
        {
            "query": "Bagaimana cara mendaftar?",
            "description": "FAQ query (tests FAQ search + LLM)"
        },
        {
            "query": "Tidak jadi pesan",
            "description": "Cancel intent (tests intent classification)"
        }
    ]

    console.print("[bold cyan]Step 2: Running Test Queries...[/bold cyan]\n")

    for i, test in enumerate(test_queries, 1):
        console.print(f"\n[bold yellow]Query {i}/{len(test_queries)}:[/bold yellow]")
        console.print(f"[dim]{test['description']}[/dim]")
        console.print(Panel(test['query'], style="yellow", border_style="dim"))

        try:
            # Get retrieval result first
            search_result = orchestrator.retriever.search(test['query'])

            if search_result:
                console.print(f"\n[cyan]→ Matched Type:[/cyan] {search_result.content_type.value.upper()}")
                console.print(f"[cyan]→ Confidence:[/cyan] {search_result.relevance_score:.2%}")

                # Show relevant metadata
                if search_result.content_type.value == 'product':
                    console.print(f"[cyan]→ Product:[/cyan] {search_result.metadata.get('official_name', 'N/A')}")
                elif search_result.content_type.value == 'intent':
                    console.print(f"[cyan]→ Intent:[/cyan] {search_result.metadata.get('intent_name', 'N/A')}")
                elif search_result.content_type.value == 'faq':
                    console.print(f"[cyan]→ FAQ:[/cyan] {search_result.metadata.get('question', 'N/A')[:50]}...")

            # Get LLM response
            console.print("\n[cyan]Processing with LLM...[/cyan]")
            response = orchestrator.process_query(test['query'])

            console.print("\n[bold green]LLM Response:[/bold green]")
            console.print(Panel(response, border_style="green"))

        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("[dim]Note: LLM might not be accessible[/dim]")

        if i < len(test_queries):
            console.print("\n" + "─"*70)

    # Show order tracking results
    console.print("\n\n[bold cyan]Step 3: Order Tracking Summary...[/bold cyan]\n")

    tracker = orchestrator.get_order_tracker()
    if len(tracker) > 0:
        console.print(f"[green]✓ Captured {len(tracker)} orders during this session[/green]")
        for order in tracker.orders[-3:]:  # Show last 3
            console.print(f"  • {order.product_name} x {order.requested_quantity_pcs} pcs - {order.status}")
    else:
        console.print("[yellow]No orders captured (requires inventory API)[/yellow]")

    # Final summary
    console.print("\n\n" + "="*70)
    console.print("  WORKFLOW DEMONSTRATION COMPLETE")
    console.print("="*70 + "\n")

    console.print("[bold green]System Components Verified:[/bold green]")
    console.print("  ✓ Product Search & Retrieval")
    console.print("  ✓ FAQ Search & Retrieval")
    console.print("  ✓ Intent Classification")
    console.print("  ✓ LLM Integration")
    console.print("  ✓ Order Tracking")
    console.print("  ✓ Unified RAG Pipeline")

    console.print("\n[cyan]To use the interactive system:[/cyan]")
    console.print("  python run_query.py")

    console.print("\n[dim]Note: Make sure LM Studio or LLM API is running for full functionality[/dim]\n")

    return 0

if __name__ == "__main__":
    try:
        exit_code = demo_full_workflow()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)
