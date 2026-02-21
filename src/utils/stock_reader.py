"""
Stock Data Reader Module.

This module provides utilities for reading and querying stock data
directly from CSV files, replacing the previous API-based approach.

Features:
- Direct CSV reading
- Stock availability checks
- Warehouse-based inventory queries
- Simple and efficient data access

Usage:
    from src.utils.stock_reader import StockReader

    reader = StockReader()
    result = reader.check_availability("IR001", 120)
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class StockCheckResult:
    """
    Result of a stock availability check.

    Attributes:
        status (str): Status of the check (success/partial/error)
        available (bool): Whether requested quantity is available
        sku (str): Product SKU checked
        requested_quantity (int): Quantity requested
        available_quantity (int): Quantity actually available
        warehouse (Optional[str]): Warehouse where stock is available
        message (str): Human-readable status message
    """
    status: str
    available: bool
    sku: str
    requested_quantity: int
    available_quantity: int
    warehouse: Optional[str]
    message: str


class StockReader:
    """
    Reads and queries stock data from CSV file.

    This class provides methods to check stock availability and
    retrieve inventory information directly from the stock_data.csv file.

    Attributes:
        stock_data (pd.DataFrame): Loaded stock inventory data
        stock_file_path (Path): Path to the stock data CSV file
    """

    def __init__(self, stock_file_path: Optional[Path] = None):
        """
        Initializes the stock reader and loads stock data.

        Args:
            stock_file_path (Optional[Path]): Path to stock data CSV.
                If None, uses default path: data/stock_data.csv

        Raises:
            FileNotFoundError: If stock data file doesn't exist
            ValueError: If stock data format is invalid
        """
        if stock_file_path is None:
            # Default path: project_root/data/stock_data.csv
            project_root = Path(__file__).parent.parent.parent
            stock_file_path = project_root / "data" / "stock_data.csv"

        self.stock_file_path = stock_file_path
        self.stock_data = None
        self._load_stock_data()

    def _load_stock_data(self) -> None:
        """
        Loads and validates stock data from CSV file.

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.stock_file_path.exists():
            raise FileNotFoundError(
                f"Stock data file not found: {self.stock_file_path}. "
                f"Please ensure stock_data.csv exists in the data directory."
            )

        try:
            self.stock_data = pd.read_csv(self.stock_file_path)

            # Validate required columns
            required_columns = [
                'sku', 'product_name', 'warehouse_id', 'warehouse_name',
                'location', 'quantity', 'reserved_quantity', 'reorder_level'
            ]
            missing_columns = [
                col for col in required_columns
                if col not in self.stock_data.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Missing required columns in stock data: {missing_columns}"
                )

        except Exception as e:
            raise ValueError(f"Failed to load stock data: {str(e)}")

    def check_availability(
        self,
        sku: str,
        requested_quantity: int,
        warehouse_id: Optional[str] = None
    ) -> StockCheckResult:
        """
        Checks stock availability for a specific quantity request.

        Args:
            sku (str): Product SKU to check
            requested_quantity (int): Quantity requested
            warehouse_id (Optional[str]): Specific warehouse to check

        Returns:
            StockCheckResult: Detailed availability information

        Note:
            If warehouse_id is provided, only checks that warehouse.
            Otherwise, checks all warehouses and selects the best option.
        """
        # Filter stock data for this SKU
        product_stocks = self.stock_data[self.stock_data['sku'] == sku]

        if product_stocks.empty:
            return StockCheckResult(
                status="error",
                available=False,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=0,
                warehouse=None,
                message=f"Product with SKU {sku} not found in inventory."
            )

        # If specific warehouse requested
        if warehouse_id:
            warehouse_stock = product_stocks[
                product_stocks['warehouse_id'] == warehouse_id
            ]

            if warehouse_stock.empty:
                return StockCheckResult(
                    status="error",
                    available=False,
                    sku=sku,
                    requested_quantity=requested_quantity,
                    available_quantity=0,
                    warehouse=warehouse_id,
                    message=f"Warehouse {warehouse_id} not found or has no stock for this product."
                )

            row = warehouse_stock.iloc[0]
            available_qty = row['quantity'] - row['reserved_quantity']
            warehouse_name = row['warehouse_name']
        else:
            # Check across all warehouses
            # Calculate available quantity per warehouse
            product_stocks = product_stocks.copy()
            product_stocks['available'] = (
                product_stocks['quantity'] - product_stocks['reserved_quantity']
            )

            # Total available across all warehouses
            total_available = product_stocks['available'].sum()

            # Find warehouse with most stock
            best_warehouse = product_stocks.loc[
                product_stocks['available'].idxmax()
            ]

            available_qty = int(total_available)
            warehouse_name = best_warehouse['warehouse_name']

        # Determine availability status
        if available_qty >= requested_quantity:
            return StockCheckResult(
                status="success",
                available=True,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=available_qty,
                warehouse=warehouse_name,
                message=f"Stok {sku} sebanyak {requested_quantity} pcs tersedia di {warehouse_name}. Silakan lanjutkan pembayaran."
            )
        elif available_qty > 0:
            return StockCheckResult(
                status="partial",
                available=True,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=available_qty,
                warehouse=warehouse_name,
                message=f"Stok {sku} sejumlah {requested_quantity} pcs tidak tersedia. Maksimal tersedia {available_qty} pcs di {warehouse_name}."
            )
        else:
            return StockCheckResult(
                status="error",
                available=False,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=0,
                warehouse=warehouse_name,
                message=f"Stok {sku} habis. Produk sedang dalam proses pengisian ulang."
            )

    def get_stock_info(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves complete stock information for a given SKU.

        Args:
            sku (str): Product SKU to query

        Returns:
            dict or None: Stock information if found, None otherwise
        """
        product_stocks = self.stock_data[self.stock_data['sku'] == sku]

        if product_stocks.empty:
            return None

        # Aggregate stock across warehouses
        total_quantity = int(product_stocks['quantity'].sum())
        total_reserved = int(product_stocks['reserved_quantity'].sum())
        available_quantity = total_quantity - total_reserved

        # Get warehouse distribution
        warehouses = []
        for _, row in product_stocks.iterrows():
            warehouse_available = row['quantity'] - row['reserved_quantity']
            warehouses.append({
                'warehouse_id': row['warehouse_id'],
                'warehouse_name': row['warehouse_name'],
                'location': row['location'],
                'available_quantity': max(0, int(warehouse_available))
            })

        return {
            'sku': sku,
            'product_name': product_stocks.iloc[0]['product_name'],
            'total_quantity': total_quantity,
            'reserved_quantity': total_reserved,
            'available_quantity': max(0, available_quantity),
            'reorder_level': int(product_stocks.iloc[0]['reorder_level']),
            'warehouses': warehouses
        }

    def to_api_response_format(self, result: StockCheckResult) -> Dict[str, Any]:
        """
        Converts StockCheckResult to API-compatible response format.

        This method ensures compatibility with existing code that expects
        API response format.

        Args:
            result (StockCheckResult): Stock check result

        Returns:
            dict: API-compatible response dictionary
        """
        return {
            'status': result.status,
            'available': result.available,
            'sku': result.sku,
            'requested_quantity': result.requested_quantity,
            'available_quantity': result.available_quantity,
            'warehouse': result.warehouse,
            'message': result.message
        }


# ============================================================================
# MODULE EXECUTION FOR TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test scenarios for stock reader.
    """
    import sys
    from rich.console import Console
    from rich.table import Table

    # Fix Windows encoding for Unicode characters
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    console = Console()

    console.print("\n[bold cyan]Testing Stock Reader[/bold cyan]\n")

    try:
        # Initialize reader
        reader = StockReader()
        console.print("[green]✅ Stock data loaded successfully[/green]")
        console.print(f"[dim]Total rows: {len(reader.stock_data)}[/dim]\n")

        # Test scenarios
        test_cases = [
            ("IR001", 120, None),  # Should succeed
            ("IR001", 2000, None),  # Should be partial
            ("INVALID", 10, None),  # Should error
            ("IG002", 50, "WH001"),  # Specific warehouse
        ]

        for sku, qty, warehouse in test_cases:
            console.print(f"[bold]Testing: SKU={sku}, Qty={qty}, Warehouse={warehouse or 'ANY'}[/bold]")

            result = reader.check_availability(sku, qty, warehouse)

            # Create result table
            table = Table(show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Status", result.status)
            table.add_row("Available", str(result.available))
            table.add_row("SKU", result.sku)
            table.add_row("Requested", str(result.requested_quantity))
            table.add_row("Available Qty", str(result.available_quantity))
            table.add_row("Warehouse", result.warehouse or "N/A")
            table.add_row("Message", result.message)

            console.print(table)
            console.print()

        # Test stock info retrieval
        console.print("[bold]Testing get_stock_info for IR001:[/bold]")
        info = reader.get_stock_info("IR001")
        if info:
            console.print(f"  Product: {info['product_name']}")
            console.print(f"  Total Quantity: {info['total_quantity']}")
            console.print(f"  Available: {info['available_quantity']}")
            console.print(f"  Warehouses: {len(info['warehouses'])}")

        console.print("\n[green]✅ All tests completed[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
