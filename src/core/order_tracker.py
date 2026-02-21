"""
Order Tracking and Data Export Module.

This module provides functionality to capture, store, and export
order information processed by the RAG system. It enables integration
with external systems like ERP, inventory management, or analytics platforms.

Features:
- Structured order data capture
- Multiple export formats (JSON, CSV, dict)
- Order history tracking
- Integration-ready data structures

Usage:
    from order_tracker import OrderTracker

    tracker = OrderTracker()
    tracker.save_order(order_data)
    tracker.export_to_json("database/orders.json")
"""

import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class OrderStatus(Enum):
    """
    Enumeration of possible order statuses.

    Attributes:
        PENDING: Order captured, awaiting processing
        AVAILABLE: Stock confirmed available
        PARTIAL: Partial stock available
        UNAVAILABLE: Stock not available
        ERROR: Error during processing
    """
    PENDING = "pending"
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class OrderData:
    """
    Structured data class for order information.

    Attributes:
        order_id (str): Unique order identifier
        timestamp (str): Order timestamp (ISO format)
        user_query (str): Original user query
        sku (str): Product SKU
        product_name (str): Official product name
        requested_quantity_pcs (int): Requested quantity in pieces
        requested_quantity_packages (float): Requested quantity in packages (dus/karton)
        package_type (str): Type of package (dus, karton, renteng, etc.)
        package_size (int): Number of pieces per package
        available_quantity_pcs (int): Available quantity in pieces
        warehouse_id (str): Warehouse identifier
        warehouse_name (str): Human-readable warehouse name
        warehouse_location (str): Warehouse location/address
        status (str): Order status
        message (str): Status message or notes
    """
    order_id: str
    timestamp: str
    user_query: str
    sku: str
    product_name: str
    requested_quantity_pcs: int
    requested_quantity_packages: float
    package_type: str
    package_size: int
    available_quantity_pcs: int
    warehouse_id: Optional[str]
    warehouse_name: Optional[str]
    warehouse_location: Optional[str]
    status: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts order data to dictionary.

        Returns:
            dict: Order data as dictionary
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Converts order data to JSON string.

        Returns:
            str: Order data as JSON
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class OrderTracker:
    """
    Tracks and manages order data for integration with external systems.

    This class provides methods to save, retrieve, and export order information
    in various formats suitable for different integration scenarios.

    Attributes:
        orders (List[OrderData]): List of tracked orders
        storage_file (Path): Path to persistent storage file
    """

    def __init__(self, storage_file: str = "database/orders.json"):
        """
        Initializes the order tracker.

        Args:
            storage_file (str): Path to JSON file for persistent storage
        """
        self.orders: List[OrderData] = []
        self.storage_file = Path(storage_file)
        self._load_orders()

    def _generate_order_id(self) -> str:
        """
        Generates a unique order identifier.

        Returns:
            str: Unique order ID with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(self.orders) + 1
        return f"ORD-{timestamp}-{count:04d}"

    def _parse_package_info(self, pack_size_desc: str) -> tuple[str, int]:
        """
        Parses package size description to extract type and size.

        Args:
            pack_size_desc (str): Package description (e.g., "1 dus = 40 pcs")

        Returns:
            tuple: (package_type, package_size)

        Example:
            "1 dus = 40 pcs" -> ("dus", 40)
            "1 karton = 48 kaleng" -> ("karton", 48)
        """
        try:
            # Parse format: "1 dus = 40 pcs"
            parts = pack_size_desc.lower().split('=')

            if len(parts) == 2:
                # Extract package type
                package_type = parts[0].strip().split()[-1]  # Get last word (dus, karton, etc.)

                # Extract package size (number)
                size_part = parts[1].strip().split()[0]  # Get first word (number)
                package_size = int(size_part)

                return package_type, package_size

        except Exception:
            pass

        # Default fallback
        return "dus", 1

    def save_order(
            self,
            user_query: str,
            product_metadata: Dict[str, Any],
            requested_quantity_pcs: int,
            api_response: Dict[str, Any]
    ) -> OrderData:
        """
        Saves order information with structured data.

        Args:
            user_query (str): Original user query
            product_metadata (dict): Product information from retrieval
            requested_quantity_pcs (int): Requested quantity in pieces
            api_response (dict): Response from inventory API

        Returns:
            OrderData: Saved order data object
        """
        # Generate order ID
        order_id = self._generate_order_id()

        # Extract product information
        sku = product_metadata.get('sku', 'UNKNOWN')
        product_name = product_metadata.get('official_name', 'Unknown Product')
        pack_size_desc = product_metadata.get('pack_size_desc', '1 dus = 1 pcs')

        # Parse package information
        package_type, package_size = self._parse_package_info(pack_size_desc)

        # Calculate package quantity
        requested_quantity_packages = requested_quantity_pcs / package_size if package_size > 0 else 0

        # Extract inventory information
        available_quantity_pcs = api_response.get('available_quantity', 0)
        warehouse_name = api_response.get('warehouse', None)

        # Determine warehouse details (if available in API response)
        warehouse_id = api_response.get('warehouse_id', None)
        warehouse_location = api_response.get('warehouse_location', None)

        # Determine status
        status_map = {
            'success': OrderStatus.AVAILABLE.value,
            'partial': OrderStatus.PARTIAL.value,
            'error': OrderStatus.UNAVAILABLE.value
        }
        status = status_map.get(api_response.get('status', 'error'), OrderStatus.ERROR.value)

        # Create order data
        order = OrderData(
            order_id=order_id,
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            sku=sku,
            product_name=product_name,
            requested_quantity_pcs=requested_quantity_pcs,
            requested_quantity_packages=round(requested_quantity_packages, 2),
            package_type=package_type,
            package_size=package_size,
            available_quantity_pcs=available_quantity_pcs,
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name,
            warehouse_location=warehouse_location,
            status=status,
            message=api_response.get('message', '')
        )

        # Add to orders list
        self.orders.append(order)

        # Save to persistent storage
        self._save_orders()

        return order

    def get_order_by_id(self, order_id: str) -> Optional[OrderData]:
        """
        Retrieves an order by its ID.

        Args:
            order_id (str): Order identifier

        Returns:
            OrderData or None: Order data if found, None otherwise
        """
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def get_orders_by_sku(self, sku: str) -> List[OrderData]:
        """
        Retrieves all orders for a specific SKU.

        Args:
            sku (str): Product SKU

        Returns:
            List[OrderData]: List of orders for the SKU
        """
        return [order for order in self.orders if order.sku == sku]

    def get_orders_by_status(self, status: str) -> List[OrderData]:
        """
        Retrieves all orders with a specific status.

        Args:
            status (str): Order status

        Returns:
            List[OrderData]: List of orders with the status
        """
        return [order for order in self.orders if order.status == status]

    def get_recent_orders(self, limit: int = 10) -> List[OrderData]:
        """
        Retrieves the most recent orders.

        Args:
            limit (int): Maximum number of orders to return

        Returns:
            List[OrderData]: List of recent orders
        """
        return self.orders[-limit:]

    def _load_orders(self) -> None:
        """
        Loads orders from persistent storage file.
        """
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.orders = [OrderData(**order) for order in data]
            except Exception as e:
                print(f"Warning: Could not load orders from {self.storage_file}: {e}")
                self.orders = []

    def _save_orders(self) -> None:
        """
        Saves orders to persistent storage file.
        """
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                data = [order.to_dict() for order in self.orders]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save orders to {self.storage_file}: {e}")

    def export_to_json(self, filepath: str) -> bool:
        """
        Exports all orders to a JSON file.

        Args:
            filepath (str): Path to output JSON file

        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                data = [order.to_dict() for order in self.orders]
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    def export_to_csv(self, filepath: str) -> bool:
        """
        Exports all orders to a CSV file.

        Args:
            filepath (str): Path to output CSV file

        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            if not self.orders:
                print("No orders to export")
                return False

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.orders[0].to_dict().keys())
                writer.writeheader()
                for order in self.orders:
                    writer.writerow(order.to_dict())
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_dict_list(self) -> List[Dict[str, Any]]:
        """
        Exports all orders as a list of dictionaries.

        Returns:
            List[dict]: List of order dictionaries

        Note:
            Useful for direct integration with other Python systems.
        """
        return [order.to_dict() for order in self.orders]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Generates summary statistics for all orders.

        Returns:
            dict: Summary statistics including counts by status, top products, etc.
        """
        if not self.orders:
            return {"total_orders": 0}

        # Count by status
        status_counts = {}
        for order in self.orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1

        # Count by SKU
        sku_counts = {}
        for order in self.orders:
            sku_counts[order.sku] = sku_counts.get(order.sku, 0) + 1

        # Total quantities
        total_pcs_requested = sum(order.requested_quantity_pcs for order in self.orders)
        total_packages_requested = sum(order.requested_quantity_packages for order in self.orders)

        return {
            "total_orders": len(self.orders),
            "status_breakdown": status_counts,
            "top_products": sorted(sku_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_pieces_requested": total_pcs_requested,
            "total_packages_requested": round(total_packages_requested, 2),
        }

    def clear_all_orders(self) -> None:
        """
        Clears all orders from memory and storage.

        Warning:
            This action cannot be undone.
        """
        self.orders = []
        self._save_orders()

    def __len__(self) -> int:
        """Returns the number of tracked orders."""
        return len(self.orders)

    def __repr__(self) -> str:
        """Returns string representation of the tracker."""
        return f"OrderTracker(orders={len(self.orders)})"