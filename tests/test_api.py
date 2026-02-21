"""
API Testing Script for Inventory Management API.

This script provides a convenient way to test all API endpoints
with predefined test cases and clear output formatting.

Usage:
    python test_api.py

    Or test specific endpoint:
    python test_api.py --endpoint health
    python test_api.py --endpoint check
"""

import requests
import json
import sys
import argparse
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize rich console
console = Console()

# API Configuration
API_BASE_URL = "http://localhost:8000"
"""Base URL for the inventory API."""

API_TIMEOUT = 10
"""Request timeout in seconds."""


class APITester:
    """
    Handles testing of all inventory API endpoints.

    Provides methods to test each endpoint with various scenarios
    and displays results in a formatted, readable way.

    Attributes:
        base_url (str): Base URL of the API
        timeout (int): Request timeout
    """

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT):
        """
        Initializes the API tester.

        Args:
            base_url (str): Base URL of the inventory API
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.test_results = []

    def check_connection(self) -> bool:
        """
        Checks if the API is accessible.

        Returns:
            bool: True if API is accessible, False otherwise
        """
        console.print("\n[bold cyan]🔍 Checking API Connection...[/bold cyan]")

        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )

            if response.status_code == 200:
                console.print("[green]✅ API is accessible and healthy[/green]")
                data = response.json()
                console.print(f"[dim]Version: {data.get('version', 'Unknown')}[/dim]")
                console.print(f"[dim]Products: {data.get('total_products', 'Unknown')}[/dim]")
                console.print(f"[dim]Warehouses: {data.get('total_warehouses', 'Unknown')}[/dim]")
                return True
            else:
                console.print(f"[yellow]⚠️  API responded with status {response.status_code}[/yellow]")
                return False

        except requests.exceptions.ConnectionError:
            console.print("[red]❌ Cannot connect to API[/red]")
            console.print(f"[yellow]Please ensure the API is running at {self.base_url}[/yellow]")
            console.print("[yellow]Start with: python stock_api.py[/yellow]")
            return False

        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            return False

    def test_health_check(self) -> None:
        """
        Tests the health check endpoint.

        Endpoint: GET /health
        """
        console.print("\n[bold cyan]📋 Testing Health Check Endpoint[/bold cyan]")

        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)

            self._display_response(
                "GET /health",
                response,
                "Should return API health status and statistics"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_get_stock_info(self, sku: str = "IR001") -> None:
        """
        Tests getting stock information for a product.

        Args:
            sku (str): Product SKU to query

        Endpoint: GET /api/v1/inventory/{sku}
        """
        console.print(f"\n[bold cyan]📦 Testing Get Stock Info Endpoint (SKU: {sku})[/bold cyan]")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/inventory/{sku}",
                timeout=self.timeout
            )

            self._display_response(
                f"GET /api/v1/inventory/{sku}",
                response,
                "Should return complete stock information including warehouse distribution"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_check_availability(
        self,
        sku: str = "IR001",
        quantity: int = 80,
        warehouse_id: Optional[str] = None
    ) -> None:
        """
        Tests stock availability checking.

        Args:
            sku (str): Product SKU to check
            quantity (int): Requested quantity
            warehouse_id (Optional[str]): Specific warehouse to check

        Endpoint: POST /api/v1/inventory/check
        """
        console.print(f"\n[bold cyan]✔️  Testing Stock Availability Check[/bold cyan]")
        console.print(f"[dim]SKU: {sku}, Quantity: {quantity}[/dim]")

        payload = {
            "sku": sku,
            "requested_quantity": quantity
        }

        if warehouse_id:
            payload["warehouse_id"] = warehouse_id
            console.print(f"[dim]Warehouse: {warehouse_id}[/dim]")

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/inventory/check",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            self._display_response(
                "POST /api/v1/inventory/check",
                response,
                "Should return availability status with warehouse information",
                payload
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_list_products(self) -> None:
        """
        Tests listing all products.

        Endpoint: GET /api/v1/products
        """
        console.print("\n[bold cyan]📋 Testing List Products Endpoint[/bold cyan]")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/products",
                timeout=self.timeout
            )

            self._display_response(
                "GET /api/v1/products",
                response,
                "Should return list of all product SKUs"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_list_warehouses(self) -> None:
        """
        Tests listing all warehouses.

        Endpoint: GET /api/v1/warehouses
        """
        console.print("\n[bold cyan]🏭 Testing List Warehouses Endpoint[/bold cyan]")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/warehouses",
                timeout=self.timeout
            )

            self._display_response(
                "GET /api/v1/warehouses",
                response,
                "Should return list of all warehouses with their information"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_invalid_sku(self) -> None:
        """
        Tests error handling for invalid SKU.

        Endpoint: GET /api/v1/inventory/{sku}
        """
        console.print("\n[bold cyan]⚠️  Testing Error Handling (Invalid SKU)[/bold cyan]")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/inventory/INVALID999",
                timeout=self.timeout
            )

            self._display_response(
                "GET /api/v1/inventory/INVALID999",
                response,
                "Should return 404 error for non-existent SKU"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def test_large_quantity(self) -> None:
        """
        Tests partial availability scenario.

        Endpoint: POST /api/v1/inventory/check
        """
        console.print("\n[bold cyan]📊 Testing Partial Availability (Large Order)[/bold cyan]")

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/inventory/check",
                json={
                    "sku": "MS010",
                    "requested_quantity": 5000  # Very large order
                },
                timeout=self.timeout
            )

            self._display_response(
                "POST /api/v1/inventory/check",
                response,
                "Should return partial availability with suggested alternatives"
            )

        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")

    def _display_response(
        self,
        endpoint: str,
        response: requests.Response,
        description: str,
        request_body: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Displays formatted API response.

        Args:
            endpoint (str): API endpoint tested
            response (requests.Response): HTTP response object
            description (str): Test description
            request_body (Optional[Dict]): Request body if POST request
        """
        # Status indicator
        if response.status_code == 200:
            status_icon = "✅"
            status_color = "green"
        elif response.status_code == 404:
            status_icon = "⚠️"
            status_color = "yellow"
        else:
            status_icon = "❌"
            status_color = "red"

        console.print(f"\n[{status_color}]{status_icon} Status: {response.status_code}[/{status_color}]")
        console.print(f"[dim]{description}[/dim]")

        # Request details
        if request_body:
            console.print("\n[bold]Request Body:[/bold]")
            console.print(Panel(
                json.dumps(request_body, indent=2),
                border_style="blue"
            ))

        # Response
        console.print("\n[bold]Response:[/bold]")
        try:
            response_json = response.json()
            formatted_response = json.dumps(response_json, indent=2, ensure_ascii=False)
            console.print(Panel(
                formatted_response,
                border_style="green" if response.status_code == 200 else "yellow"
            ))
        except:
            console.print(Panel(
                response.text,
                border_style="red"
            ))

    def run_all_tests(self) -> None:
        """
        Runs all API tests in sequence.

        Tests all endpoints with various scenarios and displays
        a comprehensive test report at the end.
        """
        console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
        console.print("[bold magenta]       Inventory API - Complete Test Suite       [/bold magenta]")
        console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

        # Check connection first
        if not self.check_connection():
            console.print("\n[red]Cannot proceed with tests. Please start the API first.[/red]")
            return

        # Run all tests
        tests = [
            ("Health Check", lambda: self.test_health_check()),
            ("Get Stock Info (IR001)", lambda: self.test_get_stock_info("IR001")),
            ("Get Stock Info (TK005)", lambda: self.test_get_stock_info("TK005")),
            ("Check Availability (Small Order)", lambda: self.test_check_availability("IR001", 80)),
            ("Check Availability (Large Order)", lambda: self.test_large_quantity()),
            ("Check Availability (Specific Warehouse)",
             lambda: self.test_check_availability("SR003", 50, "WH002")),
            ("List All Products", lambda: self.test_list_products()),
            ("List All Warehouses", lambda: self.test_list_warehouses()),
            ("Error Handling (Invalid SKU)", lambda: self.test_invalid_sku()),
        ]

        for i, (test_name, test_func) in enumerate(tests, 1):
            console.print(f"\n[bold blue]{'─' * 70}[/bold blue]")
            console.print(f"[bold blue]Test {i}/{len(tests)}: {test_name}[/bold blue]")
            console.print(f"[bold blue]{'─' * 70}[/bold blue]")

            try:
                test_func()
            except Exception as e:
                console.print(f"[red]Test failed with error: {e}[/red]")

            # Pause between tests for readability
            if i < len(tests):
                console.print("\n[dim]Press Enter to continue to next test...[/dim]", end="")
                input()

        # Test summary
        console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
        console.print("[bold green]✨ All API tests completed! ✨[/bold green]")
        console.print("[bold green]" + "=" * 70 + "[/bold green]")
        console.print("\n[cyan]💡 Next Steps:[/cyan]")
        console.print("  1. Review the test results above")
        console.print("  2. Check API documentation: http://localhost:8000/docs")
        console.print("  3. Integrate with RAG system: python llm_processor.py")


def main():
    """
    Main execution function with command-line argument support.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Test the Inventory Management API endpoints"
    )
    parser.add_argument(
        "--endpoint",
        choices=["all", "health", "stock", "check", "products", "warehouses"],
        default="all",
        help="Specific endpoint to test (default: all)"
    )
    parser.add_argument(
        "--sku",
        default="IR001",
        help="SKU to use for testing (default: IR001)"
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=80,
        help="Quantity to test (default: 80)"
    )
    parser.add_argument(
        "--url",
        default=API_BASE_URL,
        help=f"API base URL (default: {API_BASE_URL})"
    )

    args = parser.parse_args()

    try:
        tester = APITester(base_url=args.url)

        if args.endpoint == "all":
            tester.run_all_tests()
        elif args.endpoint == "health":
            tester.check_connection()
            tester.test_health_check()
        elif args.endpoint == "stock":
            tester.check_connection()
            tester.test_get_stock_info(args.sku)
        elif args.endpoint == "check":
            tester.check_connection()
            tester.test_check_availability(args.sku, args.quantity)
        elif args.endpoint == "products":
            tester.check_connection()
            tester.test_list_products()
        elif args.endpoint == "warehouses":
            tester.check_connection()
            tester.test_list_warehouses()

        return 0

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Tests interrupted by user[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal Error:[/bold red] {str(e)}")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)