"""
Working Order Tracking Demo.

This script demonstrates order tracking with explicit function calling
to ensure orders are captured even if the LLM doesn't automatically
trigger function calls.

Usage:
    python working_order_demo.py
"""

from src.core.orchestrator import UnifiedRAGOrchestrator
from src.core.order_tracker import OrderTracker
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys
import os

# Fix Windows console encoding for emojis
if os.name == 'nt':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

console = Console()


def manual_order_capture_example():
    """
    Demonstrates manual order capture when LLM doesn't trigger function calling.

    This bypasses the LLM's function calling and directly saves order data
    to the tracker.
    """
    console.print("\n[bold cyan]Manual Order Capture Example[/bold cyan]")
    console.print("[dim]Directly saving order data without relying on LLM function calling[/dim]\n")

    # Initialize orchestrator
    orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
    tracker = orchestrator.get_order_tracker()

    # Example 1: Manual order capture
    console.print("[yellow]Scenario:[/yellow] User says 'Mau beli 3 dus Indomie kuning'")

    # Retrieve product
    search_result = orchestrator.retriever.search("Indomie kuning")

    if search_result:
        product_metadata = search_result.metadata
        console.print(f"[green]✅ Found product:[/green] {product_metadata['official_name']}")

        # Extract quantity (3 dus = 3 * 40 pcs = 120 pcs)
        requested_quantity_pcs = 3 * 40  # 3 dus, 40 pcs per dus

        # Simulate API call (or call real API if available)
        if orchestrator.inventory_client:
            console.print("[cyan]📡 Checking inventory API...[/cyan]")
            api_response = orchestrator.inventory_client.check_inventory(
                sku=product_metadata['sku'],
                requested_quantity=requested_quantity_pcs
            )
        else:
            # Simulate API response if API not available
            api_response = {
                "status": "available",
                "available": True,
                "sku": product_metadata['sku'],
                "requested_quantity": requested_quantity_pcs,
                "available_quantity": 890,
                "warehouse": "Gudang A",
                "warehouse_id": "WH001",
                "warehouse_location": "Jakarta Utara",
                "message": "Stok tersedia"
            }
            console.print("[yellow]⚠️  Using simulated API response (API not running)[/yellow]")

        # Manually save order
        order = tracker.save_order(
            user_query="Mau beli 3 dus Indomie kuning",
            product_metadata=product_metadata,
            requested_quantity_pcs=requested_quantity_pcs,
            api_response=api_response
        )

        console.print(f"\n[bold green]📦 Order Saved Successfully![/bold green]")
        console.print(f"[cyan]Order ID:[/cyan] {order.order_id}")
        console.print(f"[cyan]SKU:[/cyan] {order.sku}")
        console.print(f"[cyan]Product:[/cyan] {order.product_name}")
        console.print(
            f"[cyan]Quantity:[/cyan] {order.requested_quantity_pcs} pcs ({order.requested_quantity_packages} {order.package_type})")
        console.print(f"[cyan]Warehouse:[/cyan] {order.warehouse_name} - {order.warehouse_location}")
        console.print(f"[cyan]Status:[/cyan] {order.status}")

    # Example 2: Another order
    console.print("\n[yellow]Scenario:[/yellow] User says 'Pesan 2 karton susu bendera cokelat'")

    search_result = orchestrator.retriever.search("susu bendera cokelat")
    if search_result:
        product_metadata = search_result.metadata
        console.print(f"[green]✅ Found product:[/green] {product_metadata['official_name']}")

        # 2 karton = 2 * 48 kaleng = 96 kaleng
        requested_quantity_pcs = 2 * 48

        if orchestrator.inventory_client:
            api_response = orchestrator.inventory_client.check_inventory(
                sku=product_metadata['sku'],
                requested_quantity=requested_quantity_pcs
            )
        else:
            api_response = {
                "status": "available",
                "available": True,
                "sku": product_metadata['sku'],
                "requested_quantity": requested_quantity_pcs,
                "available_quantity": 660,
                "warehouse": "Gudang B",
                "warehouse_id": "WH002",
                "warehouse_location": "Bekasi",
                "message": "Stok tersedia"
            }
            console.print("[yellow]⚠️  Using simulated API response (API not running)[/yellow]")

        order = tracker.save_order(
            user_query="Pesan 2 karton susu bendera cokelat",
            product_metadata=product_metadata,
            requested_quantity_pcs=requested_quantity_pcs,
            api_response=api_response
        )

        console.print(f"\n[bold green]📦 Order Saved Successfully![/bold green]")
        console.print(f"[cyan]Order ID:[/cyan] {order.order_id}")
        console.print(f"[cyan]SKU:[/cyan] {order.sku}")
        console.print(f"[cyan]Product:[/cyan] {order.product_name}")
        console.print(
            f"[cyan]Quantity:[/cyan] {order.requested_quantity_pcs} pcs ({order.requested_quantity_packages} {order.package_type})")
        console.print(f"[cyan]Warehouse:[/cyan] {order.warehouse_name} - {order.warehouse_location}")
        console.print(f"[cyan]Status:[/cyan] {order.status}")

    # Example 3: One more order
    console.print("\n[yellow]Scenario:[/yellow] User says 'Butuh 5 dus sabun lifebuoy merah'")

    search_result = orchestrator.retriever.search("sabun lifebuoy merah")
    if search_result:
        product_metadata = search_result.metadata
        console.print(f"[green]✅ Found product:[/green] {product_metadata['official_name']}")

        # 5 dus = 5 * 12 botol = 60 botol
        requested_quantity_pcs = 5 * 12

        if orchestrator.inventory_client:
            api_response = orchestrator.inventory_client.check_inventory(
                sku=product_metadata['sku'],
                requested_quantity=requested_quantity_pcs
            )
        else:
            api_response = {
                "status": "available",
                "available": True,
                "sku": product_metadata['sku'],
                "requested_quantity": requested_quantity_pcs,
                "available_quantity": 920,
                "warehouse": "Gudang A",
                "warehouse_id": "WH001",
                "warehouse_location": "Jakarta Utara",
                "message": "Stok tersedia"
            }
            console.print("[yellow]⚠️  Using simulated API response (API not running)[/yellow]")

        order = tracker.save_order(
            user_query="Butuh 5 dus sabun lifebuoy merah",
            product_metadata=product_metadata,
            requested_quantity_pcs=requested_quantity_pcs,
            api_response=api_response
        )

        console.print(f"\n[bold green]📦 Order Saved Successfully![/bold green]")
        console.print(f"[cyan]Order ID:[/cyan] {order.order_id}")
        console.print(f"[cyan]SKU:[/cyan] {order.sku}")
        console.print(f"[cyan]Product:[/cyan] {order.product_name}")
        console.print(
            f"[cyan]Quantity:[/cyan] {order.requested_quantity_pcs} pcs ({order.requested_quantity_packages} {order.package_type})")
        console.print(f"[cyan]Warehouse:[/cyan] {order.warehouse_name} - {order.warehouse_location}")
        console.print(f"[cyan]Status:[/cyan] {order.status}")

    return tracker


def display_all_orders(tracker):
    """
    Displays all tracked orders in a formatted table.

    Args:
        tracker (OrderTracker): Order tracker instance
    """
    console.print("\n[bold cyan]📋 All Tracked Orders[/bold cyan]")

    if len(tracker) == 0:
        console.print("[yellow]No orders tracked yet[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Order ID", width=25)
    table.add_column("SKU", width=8)
    table.add_column("Product", width=30)
    table.add_column("Qty (pcs)", width=10)
    table.add_column("Qty (pkg)", width=10)
    table.add_column("Warehouse", width=15)
    table.add_column("Status", width=10)

    for order in tracker.orders:
        table.add_row(
            order.order_id,
            order.sku,
            order.product_name[:27] + "..." if len(order.product_name) > 30 else order.product_name,
            str(order.requested_quantity_pcs),
            f"{order.requested_quantity_packages} {order.package_type}",
            order.warehouse_name or "N/A",
            order.status
        )

    console.print(table)


def export_orders_demo(tracker):
    """
    Demonstrates exporting orders to various formats.

    Args:
        tracker (OrderTracker): Order tracker instance
    """
    console.print("\n[bold cyan]💾 Exporting Orders[/bold cyan]")

    # Create exports directory
    from pathlib import Path
    Path("exports").mkdir(exist_ok=True)

    # Export to JSON
    json_file = "exports/tracked_orders.json"
    if tracker.export_to_json(json_file):
        console.print(f"[green]✅ Exported to {json_file}[/green]")

    # Export to CSV
    csv_file = "exports/tracked_orders.csv"
    if tracker.export_to_csv(csv_file):
        console.print(f"[green]✅ Exported to {csv_file}[/green]")

    # Show preview
    console.print("\n[cyan]JSON Preview:[/cyan]")
    import json
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if data:
            console.print(Panel(
                json.dumps(data[0], indent=2, ensure_ascii=False),
                title="[bold]First Order Data[/bold]",
                border_style="cyan"
            ))


def analytics_demo(tracker):
    """
    Demonstrates analytics capabilities.

    Args:
        tracker (OrderTracker): Order tracker instance
    """
    console.print("\n[bold cyan]📊 Order Analytics[/bold cyan]")

    stats = tracker.get_summary_statistics()

    # Summary table
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", width=30)
    summary_table.add_column("Value", width=20)

    summary_table.add_row("Total Orders", str(stats.get('total_orders', 0)))
    summary_table.add_row("Total Pieces Requested", f"{stats.get('total_pieces_requested', 0):,}")
    summary_table.add_row("Total Packages Requested", f"{stats.get('total_packages_requested', 0):.2f}")

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
        console.print("\n[cyan]Top Products:[/cyan]")
        product_table = Table(show_header=True)
        product_table.add_column("SKU", style="cyan")
        product_table.add_column("Orders", style="white")

        for sku, count in stats['top_products']:
            product_table.add_row(sku, str(count))

        console.print(product_table)


def integration_example(tracker):
    """
    Shows how to integrate order data with external systems.

    Args:
        tracker (OrderTracker): Order tracker instance
    """
    console.print("\n[bold cyan]🔌 Integration Example[/bold cyan]")
    console.print("[dim]How to process orders in external systems[/dim]\n")

    # Get orders as dict list
    orders = tracker.export_to_dict_list()

    console.print("[cyan]Processing orders for external integration:[/cyan]\n")

    for order in orders:
        console.print(f"[yellow]Order {order['order_id']}:[/yellow]")
        console.print(f"  SKU: {order['sku']}")
        console.print(
            f"  Quantity: {order['requested_quantity_pcs']} pcs ({order['requested_quantity_packages']} {order['package_type']})")
        console.print(f"  Warehouse: {order['warehouse_name']} ({order['warehouse_location']})")
        console.print(f"  Status: {order['status']}")

        # Simulate integration
        if order['status'] == 'available':
            console.print(f"  [green]→ Sending to ERP system...[/green]")
            console.print(f"  [green]→ Creating warehouse pick ticket...[/green]")
            console.print(f"  [green]→ Updating inventory system...[/green]")

        console.print()


def main():
    """
    Main execution function.
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   Working Order Tracking Demo   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    console.print("\n[yellow]💡 Note:[/yellow] This demo uses manual order capture to ensure")
    console.print("orders are tracked regardless of LLM function calling capabilities.\n")

    try:
        # Step 1: Capture orders manually
        tracker = manual_order_capture_example()

        # Step 2: Display all orders
        display_all_orders(tracker)

        # Step 3: Export orders
        export_orders_demo(tracker)

        # Step 4: Show analytics
        analytics_demo(tracker)

        # Step 5: Integration example
        integration_example(tracker)

        # Success summary
        console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
        console.print("[bold green]✨ Order Tracking Demo Completed Successfully! ✨[/bold green]")
        console.print("[bold green]" + "=" * 70 + "[/bold green]")

        console.print("\n[cyan]📁 Generated Files:[/cyan]")
        console.print("  ✓ orders.json (persistent storage)")
        console.print("  ✓ exports/tracked_orders.json")
        console.print("  ✓ exports/tracked_orders.csv")

        console.print("\n[yellow]🔌 Integration Ready![/yellow]")
        console.print("Your order data is now ready to be integrated with:")
        console.print("  • ERP systems")
        console.print("  • Inventory management")
        console.print("  • Analytics platforms")
        console.print("  • Order processing systems")

        console.print("\n[cyan]📖 Next Steps:[/cyan]")
        console.print("  1. Check the generated JSON/CSV files")
        console.print("  2. Review ORDER_TRACKING_GUIDE.md for integration examples")
        console.print("  3. Implement your custom integration logic")

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Demo interrupted by user[/yellow]")
        sys.exit(0)