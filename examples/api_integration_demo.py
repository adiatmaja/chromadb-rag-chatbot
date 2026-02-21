"""
Example Order Integration Script.

This script demonstrates how to integrate the RAG system's order tracking
with external systems. It shows various use cases including:
- Processing orders automatically
- Exporting to different formats
- Sending data to external APIs
- Generating reports

Usage:
    python example_order_integration.py
"""

from src.core.orchestrator import UnifiedRAGOrchestrator
from src.core.order_tracker import OrderTracker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json
from datetime import datetime
from pathlib import Path

console = Console()


def example_1_basic_tracking():
    """
    Example 1: Basic order tracking.

    Demonstrates how to enable tracking and view saved orders.
    """
    console.print("\n[bold cyan]Example 1: Basic Order Tracking[/bold cyan]")
    console.print("[dim]Processing a product order and viewing the tracked data[/dim]\n")

    # Initialize with tracking enabled
    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)

    # Simulate user queries
    queries = [
        "Mau beli 3 dus Indomie kuning",
        "Pesan 2 karton susu bendera cokelat"
    ]

    for query in queries:
        console.print(f"[yellow]User Query:[/yellow] {query}")
        response = orchestrator.process_query(query)
        console.print(f"[green]Response:[/green] {response[:100]}...\n")

    # View tracked orders
    tracker = orchestrator.get_order_tracker()
    console.print(f"[cyan]Total orders tracked: {len(tracker)}[/cyan]")

    for order in tracker.get_recent_orders(limit=5):
        console.print(f"  - {order.order_id}: {order.sku} x {order.requested_quantity_pcs} pcs")


def example_2_export_data():
    """
    Example 2: Exporting order data.

    Shows how to export orders to JSON and CSV formats.
    """
    console.print("\n[bold cyan]Example 2: Exporting Order Data[/bold cyan]")
    console.print("[dim]Exporting orders to JSON and CSV files[/dim]\n")

    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    tracker = orchestrator.get_order_tracker()

    if len(tracker) == 0:
        console.print("[yellow]No orders to export. Process some queries first.[/yellow]")
        return

    # Create exports directory
    Path("exports").mkdir(exist_ok=True)

    # Export to JSON
    json_file = "exports/orders_export.json"
    if orchestrator.export_orders(json_file, format="json"):
        console.print(f"[green]✅ Exported to {json_file}[/green]")

    # Export to CSV
    csv_file = "exports/orders_export.csv"
    if orchestrator.export_orders(csv_file, format="csv"):
        console.print(f"[green]✅ Exported to {csv_file}[/green]")

    # Show file contents preview
    console.print("\n[cyan]JSON Preview:[/cyan]")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        console.print(json.dumps(data[0] if data else {}, indent=2)[:500] + "...")


def example_3_analytics():
    """
    Example 3: Order analytics and reporting.

    Demonstrates how to generate analytics from tracked orders.
    """
    console.print("\n[bold cyan]Example 3: Order Analytics[/bold cyan]")
    console.print("[dim]Generating analytics and statistics from order data[/dim]\n")

    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)

    # Display summary
    orchestrator.display_order_summary()

    # Custom analytics
    tracker = orchestrator.get_order_tracker()

    if len(tracker) > 0:
        console.print("\n[bold cyan]Custom Analytics:[/bold cyan]")

        # Calculate average order size
        total_pcs = sum(order.requested_quantity_pcs for order in tracker.orders)
        avg_pcs = total_pcs / len(tracker) if len(tracker) > 0 else 0

        console.print(f"Average order size: {avg_pcs:.1f} pcs")

        # Find most popular warehouse
        warehouse_counts = {}
        for order in tracker.orders:
            if order.warehouse_name:
                warehouse_counts[order.warehouse_name] = warehouse_counts.get(order.warehouse_name, 0) + 1

        if warehouse_counts:
            most_popular = max(warehouse_counts, key=warehouse_counts.get)
            console.print(f"Most popular warehouse: {most_popular} ({warehouse_counts[most_popular]} orders)")


def example_4_external_api_integration():
    """
    Example 4: Simulated external API integration.

    Shows how to send order data to external systems.
    """
    console.print("\n[bold cyan]Example 4: External API Integration[/bold cyan]")
    console.print("[dim]Simulating order data sent to external system[/dim]\n")

    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    tracker = orchestrator.get_order_tracker()

    if len(tracker) == 0:
        console.print("[yellow]No orders to integrate. Process some queries first.[/yellow]")
        return

    # Get orders as dict for API integration
    orders = tracker.export_to_dict_list()

    # Simulate sending to external API
    console.print("[cyan]Simulating API calls to external system...[/cyan]\n")

    for order in orders[-3:]:  # Process last 3 orders
        if order['status'] == 'available':
            # Prepare payload for external system
            payload = {
                "order_id": order['order_id'],
                "sku": order['sku'],
                "product_name": order['product_name'],
                "quantity_pcs": order['requested_quantity_pcs'],
                "quantity_packages": order['requested_quantity_packages'],
                "package_type": order['package_type'],
                "warehouse": order['warehouse_name'],
                "timestamp": order['timestamp']
            }

            console.print(f"[green]✅ Sending order {order['order_id']} to ERP system[/green]")
            console.print(f"[dim]   Payload: {json.dumps(payload, indent=2)[:150]}...[/dim]\n")

            # In real integration, you would do:
            # response = requests.post("https://your-erp.com/api/orders", json=payload)


def example_5_filtering_and_querying():
    """
    Example 5: Advanced filtering and querying.

    Demonstrates how to query orders by various criteria.
    """
    console.print("\n[bold cyan]Example 5: Advanced Querying[/bold cyan]")
    console.print("[dim]Filtering orders by SKU, status, and other criteria[/dim]\n")

    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    tracker = orchestrator.get_order_tracker()

    if len(tracker) == 0:
        console.print("[yellow]No orders to query. Process some queries first.[/yellow]")
        return

    # Query by SKU
    sku_to_find = "IR001"
    sku_orders = tracker.get_orders_by_sku(sku_to_find)
    console.print(f"[cyan]Orders for SKU {sku_to_find}:[/cyan] {len(sku_orders)}")

    # Query by status
    available_orders = tracker.get_orders_by_status("available")
    partial_orders = tracker.get_orders_by_status("partial")
    unavailable_orders = tracker.get_orders_by_status("unavailable")

    console.print(f"[green]Available orders:[/green] {len(available_orders)}")
    console.print(f"[yellow]Partial orders:[/yellow] {len(partial_orders)}")
    console.print(f"[red]Unavailable orders:[/red] {len(unavailable_orders)}")

    # Custom filtering
    console.print("\n[cyan]Large orders (>100 pcs):[/cyan]")
    large_orders = [order for order in tracker.orders if order.requested_quantity_pcs > 100]
    for order in large_orders[:5]:
        console.print(f"  - {order.order_id}: {order.requested_quantity_pcs} pcs of {order.sku}")


def example_6_report_generation():
    """
    Example 6: Generating formatted reports.

    Creates a formatted report suitable for management review.
    """
    console.print("\n[bold cyan]Example 6: Report Generation[/bold cyan]")
    console.print("[dim]Creating a formatted management report[/dim]\n")

    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    tracker = orchestrator.get_order_tracker()

    if len(tracker) == 0:
        console.print("[yellow]No orders to report. Process some queries first.[/yellow]")
        return

    # Generate report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("DAILY ORDER REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    stats = tracker.get_summary_statistics()

    report_lines.append("SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(f"Total Orders: {stats.get('total_orders', 0)}")
    report_lines.append(f"Total Pieces: {stats.get('total_pieces_requested', 0):,}")
    report_lines.append(f"Total Packages: {stats.get('total_packages_requested', 0):.2f}")
    report_lines.append("")

    report_lines.append("STATUS BREAKDOWN")
    report_lines.append("-" * 70)
    for status, count in stats.get('status_breakdown', {}).items():
        report_lines.append(f"{status.upper()}: {count} orders")
    report_lines.append("")

    report_lines.append("TOP PRODUCTS")
    report_lines.append("-" * 70)
    for i, (sku, count) in enumerate(stats.get('top_products', [])[:5], 1):
        report_lines.append(f"{i}. {sku}: {count} orders")
    report_lines.append("")

    report_lines.append("=" * 70)

    report_text = "\n".join(report_lines)

    # Display report
    console.print(Panel(report_text, title="[bold green]Management Report[/bold green]"))

    # Save report
    report_file = "exports/daily_report.txt"
    Path("exports").mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    console.print(f"\n[green]✅ Report saved to {report_file}[/green]")


def main():
    """
    Main function to run all examples.
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   Order Integration Examples   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    examples = [
        ("Basic Tracking", example_1_basic_tracking),
        ("Export Data", example_2_export_data),
        ("Analytics", example_3_analytics),
        ("External API Integration", example_4_external_api_integration),
        ("Filtering & Querying", example_5_filtering_and_querying),
        ("Report Generation", example_6_report_generation),
    ]

    for i, (name, func) in enumerate(examples, 1):
        console.print(f"\n[bold blue]{'─' * 70}[/bold blue]")
        console.print(f"[bold blue]Running Example {i}/{len(examples)}: {name}[/bold blue]")
        console.print(f"[bold blue]{'─' * 70}[/bold blue]")

        try:
            func()
        except Exception as e:
            console.print(f"[red]❌ Example failed: {e}[/red]")

        if i < len(examples):
            console.print("\n[dim]Press Enter to continue to next example...[/dim]", end="")
            input()

    console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
    console.print("[bold green]✨ All examples completed! ✨[/bold green]")
    console.print("[bold green]" + "=" * 70 + "[/bold green]")

    console.print("\n[cyan]📁 Generated Files:[/cyan]")
    console.print("  - orders.json (persistent storage)")
    console.print("  - exports/orders_export.json")
    console.print("  - exports/orders_export.csv")
    console.print("  - exports/daily_report.txt")

    console.print("\n[yellow]💡 Integration Tips:[/yellow]")
    console.print("  1. Use export_to_dict_list() for Python integrations")
    console.print("  2. Use export_to_json() for REST API integrations")
    console.print("  3. Use export_to_csv() for Excel/BI tool integrations")
    console.print("  4. Check ORDER_TRACKING_GUIDE.md for more examples")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Examples interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal Error:[/bold red] {str(e)}")
        import traceback

        console.print("[dim]" + traceback.format_exc() + "[/dim]")