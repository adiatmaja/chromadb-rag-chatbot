"""
Interactive RAG Query System.

This script provides an interactive interface to run custom queries
against the RAG system (products + FAQs).

Usage:
    python run_query.py

Commands:
    - Type your query and press Enter
    - Type 'orders' to see all tracked orders
    - Type 'stats' to see order statistics
    - Type 'export' to export orders to JSON/CSV
    - Type 'exit' or 'quit' to stop
"""
import sys
import os

# Docker compatibility - load onnxruntime mock before any chromadb imports
import load_docker_compat

# Fix Windows console encoding for Unicode characters
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.orchestrator import UnifiedRAGOrchestrator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def display_orders(tracker):
    """Display all tracked orders in a table."""
    if len(tracker) == 0:
        console.print("\n[yellow]📭 No orders tracked yet[/yellow]\n")
        return

    console.print(f"\n[bold cyan]📦 Tracked Orders ({len(tracker)} total)[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Order ID", width=25)
    table.add_column("Product", width=30)
    table.add_column("Quantity", width=15)
    table.add_column("Status", width=12)

    for order in tracker.orders:
        product_name = order.product_name[:27] + "..." if len(order.product_name) > 30 else order.product_name
        quantity = f"{order.requested_quantity_pcs} pcs"
        status_color = "green" if order.status == "available" else "red"

        table.add_row(
            order.order_id,
            product_name,
            quantity,
            f"[{status_color}]{order.status}[/{status_color}]"
        )

    console.print(table)
    console.print()


def display_stats(tracker):
    """Display order statistics."""
    if len(tracker) == 0:
        console.print("\n[yellow]📭 No orders to analyze[/yellow]\n")
        return

    stats = tracker.get_summary_statistics()

    console.print("\n[bold cyan]📊 Order Statistics[/bold cyan]\n")

    # Summary table
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", width=30)
    summary_table.add_column("Value", width=20)

    summary_table.add_row("Total Orders", str(stats.get('total_orders', 0)))
    summary_table.add_row("Total Pieces", f"{stats.get('total_pieces_requested', 0):,}")
    summary_table.add_row("Total Packages", f"{stats.get('total_packages_requested', 0):.2f}")

    console.print(summary_table)

    # Status breakdown
    if stats.get('status_breakdown'):
        console.print("\n[cyan]Status Breakdown:[/cyan]")
        status_table = Table(show_header=True)
        status_table.add_column("Status", style="cyan")
        status_table.add_column("Count", style="white")

        for status, count in stats['status_breakdown'].items():
            status_table.add_row(status.upper(), str(count))

        console.print(status_table)

    # Top products
    if stats.get('top_products'):
        console.print("\n[cyan]Most Ordered Products:[/cyan]")
        product_table = Table(show_header=True)
        product_table.add_column("SKU", style="cyan")
        product_table.add_column("Orders", style="white")

        for sku, count in stats['top_products']:
            product_table.add_row(sku, str(count))

        console.print(product_table)

    console.print()


def export_orders(tracker):
    """Export orders to JSON and CSV."""
    if len(tracker) == 0:
        console.print("\n[yellow]📭 No orders to export[/yellow]\n")
        return

    console.print("\n[cyan]💾 Exporting orders...[/cyan]")

    # Export to JSON
    json_file = "exported_orders.json"
    if tracker.export_to_json(json_file):
        console.print(f"[green]✅ Exported to {json_file}[/green]")

    # Export to CSV
    csv_file = "exported_orders.csv"
    if tracker.export_to_csv(csv_file):
        console.print(f"[green]✅ Exported to {csv_file}[/green]")

    console.print()


def print_help():
    """Print help information."""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]

• [yellow]<your query>[/yellow]     - Process any product or FAQ query
• [yellow]orders[/yellow]            - View all tracked orders
• [yellow]stats[/yellow]             - View order statistics
• [yellow]export[/yellow]            - Export orders to JSON/CSV files
• [yellow]help[/yellow]              - Show this help message
• [yellow]clear[/yellow]             - Clear the screen
• [yellow]exit[/yellow] or [yellow]quit[/yellow]   - Exit the program

[bold cyan]Example Queries:[/bold cyan]

[green]Product Orders:[/green]
  • "Mau beli 3 dus Indomie kuning"
  • "Pesan 5 karton susu bendera cokelat"
  • "Butuh 10 dus sabun lifebuoy merah"

[green]Product Information:[/green]
  • "tolong carikan sabun lifebuoy"
  • "ada teh kotak yang rasa melati?"

[green]FAQ Questions:[/green]
  • "bagaimana cara mendaftar?"
  • "metode pembayaran apa saja?"
  • "bagaimana cara tracking pesanan?"
"""
    console.print(Panel(help_text, title="[bold]Help[/bold]", border_style="cyan"))


def main():
    """Main interactive loop."""
    # Print welcome banner
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   Interactive RAG Query System   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print()

    # Initialize orchestrator
    console.print("[bold cyan]🤖 Initializing RAG System...[/bold cyan]")

    try:
        orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
        console.print("[green]✅ System ready![/green]")
        console.print("[dim]Type 'help' for available commands[/dim]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to initialize: {e}[/bold red]")
        console.print("[yellow]Make sure you have indexed the data first:[/yellow]")
        console.print("  python index_faq.py")
        return 1

    # Interactive loop
    while True:
        try:
            # Get user input
            query = input("📝 Your query: ").strip()

            # Skip empty queries
            if not query:
                continue

            # Handle commands
            if query.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break

            elif query.lower() == 'help':
                print_help()
                continue

            elif query.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif query.lower() == 'orders':
                tracker = orchestrator.get_order_tracker()
                display_orders(tracker)
                continue

            elif query.lower() == 'stats':
                tracker = orchestrator.get_order_tracker()
                display_stats(tracker)
                continue

            elif query.lower() == 'export':
                tracker = orchestrator.get_order_tracker()
                export_orders(tracker)
                continue

            # Process query through RAG
            console.print("\n[cyan]🔍 Processing query...[/cyan]")

            # First check what type of content matches
            result = orchestrator.retriever.search(query)

            if result:
                console.print(f"[dim]Matched: {result.content_type.value.upper()} (score: {result.relevance_score:.4f})[/dim]")

            # Get LLM response
            response = orchestrator.process_query(query)

            # Display response
            console.print(f"\n[bold green]💬 Response:[/bold green]")
            console.print(Panel(response, border_style="green"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break

        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")
            console.print("[dim]Check that LLM service is running and accessible[/dim]\n")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]\n")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]\n")
        sys.exit(1)
