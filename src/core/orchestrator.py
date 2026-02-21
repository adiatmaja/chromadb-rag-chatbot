"""
Unified LLM Processor and RAG Orchestration Module.

This module extends the RAG system to handle both product queries and
FAQ (Frequently Asked Questions). It intelligently routes queries to
the appropriate knowledge base and generates contextual responses.

Features:
- Unified product and FAQ search
- Intelligent query classification
- Context-aware response generation
- Function calling for inventory
- FAQ-specific formatting
- Order tracking and data capture

Usage:
    python llm_unified.py

    Or import as a module:
    from llm_unified import UnifiedRAGOrchestrator
"""

import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys

# Import configuration and retrievers
from src.config import (
    LLM_BASE_URL,
    LLM_API_KEY,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    INVENTORY_CHECK_FUNCTION,
)
from src.core.retriever import UnifiedRetriever, ContentType, SearchResult
from src.core.order_tracker import OrderTracker
from src.utils.stock_reader import StockReader

# Initialize rich console
console = Console()

# System Prompts
UNIFIED_SYSTEM_PROMPT_TEMPLATE = """
Anda adalah Asisten Penjualan E-commerce yang cerdas dan membantu pelanggan dengan profesional.

KEMAMPUAN ANDA:
1. Menjawab pertanyaan tentang produk berdasarkan katalog
2. Memberikan informasi dari FAQ (Frequently Asked Questions)
3. Mengecek ketersediaan stok produk dengan function calling

FUNCTION TOOL YANG TERSEDIA:
- check_inventory(sku: str, requested_quantity: int): Mengecek stok produk
  Gunakan tool ini HANYA jika kuantitas eksplisit disebutkan dalam pertanyaan

DATA KONTEKS YANG DIBERIKAN:
Tipe Konten: {content_type}
---
{context_data}
---

INSTRUKSI PENTING:
1. Selalu gunakan data dari konteks yang diberikan
2. Untuk PRODUK: Berikan informasi SKU, nama, ukuran kemasan
3. Untuk FAQ: Berikan jawaban lengkap sesuai dengan FAQ
4. Jika ada kuantitas dalam pertanyaan, panggil check_inventory
5. Gunakan bahasa Indonesia yang sopan dan profesional
6. Jika pertanyaan di luar konteks, jelaskan dengan sopan bahwa Anda tidak memiliki informasi tersebut

CATATAN:
- Jangan membuat informasi sendiri
- Jawab sesuai dengan tipe konten yang diberikan
- Untuk FAQ, Anda boleh menambahkan sapaan yang ramah
"""


class UnifiedRAGOrchestrator:
    """
    Orchestrates the unified RAG pipeline for products and FAQs.

    Attributes:
        retriever (UnifiedRetriever): Instance for unified retrieval
        llm_client (OpenAI): OpenAI-compatible client for LM Studio
        stock_reader (StockReader): Direct CSV reader for stock data
        order_tracker (OrderTracker): Tracks orders for external integration
        current_product_metadata (dict): Stores current product context for order tracking
    """

    def __init__(self, enable_order_tracking: bool = True):
        """
        Initializes the unified RAG orchestrator.

        Args:
            enable_order_tracking (bool): Enable order tracking and data capture

        Raises:
            ConnectionError: If unable to connect to LM Studio
        """
        console.print("\n[bold cyan]🤖 Initializing Unified RAG Orchestrator...[/bold cyan]")

        # Initialize unified retriever
        console.print("[cyan]Setting up unified retriever...[/cyan]")
        self.retriever = UnifiedRetriever()

        # Initialize LLM client
        console.print(f"[cyan]Connecting to LLM: {LLM_BASE_URL}[/cyan]")
        console.print(f"[cyan]Model: {LLM_MODEL_NAME}[/cyan]")

        self.llm_client = OpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY
        )

        # Initialize stock reader (direct CSV access)
        console.print("[cyan]Loading stock data from CSV...[/cyan]")
        try:
            self.stock_reader = StockReader()
            console.print(f"[green]✅ Stock data loaded ({len(self.stock_reader.stock_data)} entries)[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Stock data not available: {e}[/yellow]")
            self.stock_reader = None

        # Initialize order tracker
        self.order_tracker = None
        self.current_product_metadata = None

        if enable_order_tracking:
            console.print("[cyan]Initializing order tracking system...[/cyan]")
            self.order_tracker = OrderTracker()
            console.print(f"[green]✅ Order tracker ready ({len(self.order_tracker)} existing orders)[/green]")

        console.print("[green]✅ Unified RAG Orchestrator ready![/green]")

    def process_query(self, user_query: str) -> str:
        """
        Processes a user query through the unified RAG pipeline.

        Args:
            user_query (str): The user's natural language query

        Returns:
            str: Generated response from the LLM

        Pipeline steps:
        1. Unified Retrieval: Search both products and FAQs
        2. Content Classification: Determine content type
        3. Context Building: Format context for LLM
        4. LLM Inference: Generate response
        5. Function Calling (if needed): Check inventory for products
        6. Order Tracking: Save order data for external processing
        7. Response Generation: Create final natural language response
        """
        console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
        console.print(f"[bold magenta]Processing Query:[/bold magenta] {user_query}")
        console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

        # Step 1: UNIFIED RETRIEVAL
        console.print("\n[bold cyan]Step 1: Unified Retrieval (Products + FAQs)[/bold cyan]")
        search_result = self.retriever.search(user_query)

        if not search_result:
            return self._generate_no_result_response()

        # Store product metadata for order tracking
        if search_result.content_type == ContentType.PRODUCT:
            self.current_product_metadata = search_result.metadata
        else:
            self.current_product_metadata = None

        # Step 2: CONTEXT BUILDING
        console.print("\n[bold cyan]Step 2: Building Context for LLM[/bold cyan]")
        context_string, content_type_str = self._build_context_string(search_result)
        console.print(f"[dim]Content Type: {content_type_str}[/dim]")
        console.print(f"[dim]Context: {context_string[:200]}...[/dim]")

        # Step 3: LLM INFERENCE
        console.print("\n[bold cyan]Step 3: LLM Inference[/bold cyan]")
        response = self._call_llm(user_query, context_string, content_type_str)

        return response

    def _build_context_string(
        self,
        search_result: SearchResult,
        product_candidates: List[SearchResult] | None = None,
    ) -> tuple[str, str]:
        """
        Formats search result into context string for LLM.

        When product_candidates is provided (multiple products), formats them
        as a numbered list so the LLM can select the most relevant one.

        Args:
            search_result (SearchResult): Best result from unified search
            product_candidates (List[SearchResult] | None): Top N product candidates
                for reranking. If None, falls back to single-product format.

        Returns:
            tuple: (context_string, content_type_string)
        """
        content_type = search_result.content_type

        if content_type == ContentType.PRODUCT:
            candidates = product_candidates or [search_result]
            if len(candidates) == 1:
                m = candidates[0].metadata
                context = (
                    f"SKU: {m.get('sku', 'N/A')}, "
                    f"Nama Resmi: {m.get('official_name', 'N/A')}, "
                    f"Kuantitas Dus: {m.get('pack_size_desc', 'N/A')}, "
                    f"Sinonim: {m.get('colloquial_names', 'N/A')}"
                )
            else:
                lines = ["Beberapa kandidat produk yang mungkin sesuai:"]
                for i, candidate in enumerate(candidates, 1):
                    m = candidate.metadata
                    lines.append(
                        f"{i}. SKU: {m.get('sku', 'N/A')} | "
                        f"Nama: {m.get('official_name', 'N/A')} | "
                        f"Alias: {m.get('colloquial_names', 'N/A')} | "
                        f"Kemasan: {m.get('pack_size_desc', 'N/A')}"
                    )
                lines.append(
                    "\nPilih produk yang PALING SESUAI dengan pertanyaan pengguna. "
                    "Gunakan SKU dari produk terpilih jika perlu check_inventory."
                )
                context = "\n".join(lines)
            return context, "PRODUK"

        elif content_type == ContentType.FAQ:
            metadata = search_result.metadata
            context = (
                f"Pertanyaan: {metadata.get('question', 'N/A')}\n"
                f"Jawaban: {metadata.get('answer', 'N/A')}"
            )
            return context, "FAQ"

        else:
            return "Informasi tidak tersedia", "UNKNOWN"

    def _call_llm(self, user_query: str, context_data: str, content_type: str) -> str:
        """
        Calls the LLM with query and context, handling function calling if needed.

        Args:
            user_query (str): User's original query
            context_data (str): Formatted context
            content_type (str): Type of content (PRODUK/FAQ)

        Returns:
            str: LLM's response
        """
        # Build system prompt with context
        system_prompt = UNIFIED_SYSTEM_PROMPT_TEMPLATE.format(
            content_type=content_type,
            context_data=context_data
        )

        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        try:
            # Call LLM with function calling support (only for products)
            console.print("[yellow]⏳ Waiting for LLM response...[/yellow]")

            # Only enable function calling for product queries
            tools = [INVENTORY_CHECK_FUNCTION] if content_type == "PRODUK" else None

            completion = self.llm_client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                tools=tools,
                tool_choice="auto" if tools else None
            )

            # Check if model wants to call a function
            if completion.choices[0].message.tool_calls:
                console.print("[bold green]🔧 Function calling detected![/bold green]")
                return self._handle_function_calling(
                    messages,
                    completion.choices[0].message.tool_calls[0]
                )

            # No function calling, return direct response
            response = completion.choices[0].message.content
            console.print("[green]✅ LLM response generated[/green]")
            return response

        except Exception as e:
            console.print(f"[bold red]❌ LLM Error:[/bold red] {str(e)}")
            return f"Maaf, terjadi kesalahan saat memproses permintaan Anda: {str(e)}"

    def _handle_function_calling(
        self,
        messages: List[Dict[str, str]],
        tool_call: Any
    ) -> str:
        """
        Handles function calling workflow for inventory checks.

        Args:
            messages (list): Conversation history
            tool_call: Tool call object from LLM response

        Returns:
            str: Final response after function execution

        Note:
            Captures order data for external system integration when
            inventory checks are performed.
        """
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        console.print(f"[cyan]Function:[/cyan] {function_name}")
        console.print(f"[cyan]Arguments:[/cyan] {json.dumps(function_args, indent=2)}")

        # Execute function with stock reader
        if function_name == "check_inventory" and self.stock_reader:
            console.print("[cyan]📊 Checking stock from CSV data...[/cyan]")

            result = self.stock_reader.check_availability(
                sku=function_args.get('sku'),
                requested_quantity=function_args.get('requested_quantity'),
                warehouse_id=function_args.get('warehouse_id')
            )

            # Convert to API-compatible format
            api_response = self.stock_reader.to_api_response_format(result)

            console.print("[green]✅ Stock check completed[/green]")
            console.print(f"[dim]Response: {json.dumps(api_response, indent=2)}[/dim]")

            # Save order data for external processing
            if self.order_tracker and self.current_product_metadata:
                try:
                    order_data = self.order_tracker.save_order(
                        user_query=messages[1]['content'],  # Original user query
                        product_metadata=self.current_product_metadata,
                        requested_quantity_pcs=function_args.get('requested_quantity'),
                        api_response=api_response
                    )

                    console.print(f"[green]📦 Order data saved: {order_data.order_id}[/green]")
                    console.print(f"[dim]  SKU: {order_data.sku}[/dim]")
                    console.print(f"[dim]  Quantity: {order_data.requested_quantity_pcs} pcs ({order_data.requested_quantity_packages} {order_data.package_type})[/dim]")
                    console.print(f"[dim]  Warehouse: {order_data.warehouse_name}[/dim]")
                    console.print(f"[dim]  Status: {order_data.status}[/dim]")
                except Exception as e:
                    console.print(f"[yellow]⚠️  Could not save order data: {e}[/yellow]")
        else:
            api_response = {
                "status": "error",
                "message": "Stock data not available or unknown function"
            }

        console.print(f"[cyan]Stock Check Response:[/cyan] {json.dumps(api_response, indent=2)}")

        # Build updated message history
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call.model_dump()]
        })

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(api_response)
        })

        # Get final response from LLM
        console.print("[yellow]⏳ Generating final response...[/yellow]")

        final_completion = self.llm_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )

        final_response = final_completion.choices[0].message.content
        console.print("[green]✅ Final response generated[/green]")

        return final_response

    def _generate_no_result_response(self) -> str:
        """
        Generates a polite response when no content is found.

        Returns:
            str: Polite message indicating no results
        """
        return (
            "Mohon maaf, saya tidak dapat menemukan informasi yang relevan "
            "dengan pertanyaan Anda. Bisakah Anda memberikan informasi "
            "lebih detail atau mencoba dengan kata kunci yang berbeda?"
        )

    def get_order_tracker(self) -> Optional[OrderTracker]:
        """
        Returns the order tracker instance.

        Returns:
            OrderTracker or None: Order tracker if enabled, None otherwise
        """
        return self.order_tracker

    def export_orders(self, filepath: str, format: str = "json") -> bool:
        """
        Exports tracked orders to a file.

        Args:
            filepath (str): Path to output file
            format (str): Export format ('json' or 'csv')

        Returns:
            bool: True if export successful, False otherwise
        """
        if not self.order_tracker:
            console.print("[yellow]⚠️  Order tracking is not enabled[/yellow]")
            return False

        if format.lower() == "json":
            result = self.order_tracker.export_to_json(filepath)
        elif format.lower() == "csv":
            result = self.order_tracker.export_to_csv(filepath)
        else:
            console.print(f"[red]❌ Unsupported format: {format}[/red]")
            return False

        if result:
            console.print(f"[green]✅ Orders exported to {filepath}[/green]")
        else:
            console.print(f"[red]❌ Failed to export orders[/red]")

        return result

    def display_order_summary(self) -> None:
        """
        Displays a summary of tracked orders.
        """
        if not self.order_tracker:
            console.print("[yellow]⚠️  Order tracking is not enabled[/yellow]")
            return

        stats = self.order_tracker.get_summary_statistics()

        console.print("\n[bold cyan]📊 Order Summary Statistics[/bold cyan]")

        # Create summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white")

        table.add_row("Total Orders", str(stats.get("total_orders", 0)))
        table.add_row("Total Pieces Requested", str(stats.get("total_pieces_requested", 0)))
        table.add_row("Total Packages Requested", str(stats.get("total_packages_requested", 0)))

        console.print(table)

        # Status breakdown
        if "status_breakdown" in stats:
            console.print("\n[bold cyan]Status Breakdown:[/bold cyan]")
            status_table = Table(show_header=True)
            status_table.add_column("Status", style="cyan")
            status_table.add_column("Count", style="white")

            for status, count in stats["status_breakdown"].items():
                status_table.add_row(status, str(count))

            console.print(status_table)

        # Top products
        if "top_products" in stats and stats["top_products"]:
            console.print("\n[bold cyan]Top 5 Products:[/bold cyan]")
            product_table = Table(show_header=True)
            product_table.add_column("SKU", style="cyan")
            product_table.add_column("Orders", style="white")

            for sku, count in stats["top_products"]:
                product_table.add_row(sku, str(count))

            console.print(product_table)


def run_test_scenarios():
    """
    Runs comprehensive test scenarios for unified RAG system.

    Test scenarios include:
    - Product searches with quantity (triggers function calling)
    - Product information queries
    - FAQ queries
    - Mixed scenarios
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   Unified RAG System - Complete Test Suite   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    # Initialize orchestrator
    try:
        orchestrator = UnifiedRAGOrchestrator()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize orchestrator: {e}[/bold red]")
        console.print("\n[yellow]⚠️  Make sure:[/yellow]")
        console.print("  1. You have run 'python index_data.py' (for products)")
        console.print("  2. You have run 'python index_faq.py' (for FAQs)")
        console.print("  3. Stock data CSV exists: data/stock_data.csv")
        console.print("  4. LM Studio is running on http://localhost:1234")
        return 1

    # Define test scenarios
    test_scenarios = [
        {
            "name": "Product Query with Quantity",
            "query": "Mau beli 2 dus Indomie kuning",
            "expected": "Should retrieve product, call inventory API, confirm availability"
        },
        {
            "name": "FAQ Query - Registration",
            "query": "Bagaimana cara mendaftar sebagai pelanggan baru?",
            "expected": "Should retrieve FAQ and provide registration information"
        },
        {
            "name": "FAQ Query - Payment",
            "query": "Apa saja metode pembayaran yang bisa digunakan?",
            "expected": "Should retrieve FAQ about payment methods"
        },
        {
            "name": "Product Information Query",
            "query": "tolong carikan info tentang sabun lifebuoy",
            "expected": "Should provide product information without inventory check"
        },
        {
            "name": "FAQ Query - Shipping",
            "query": "berapa lama waktu pengiriman barang?",
            "expected": "Should retrieve FAQ about delivery times"
        },
        {
            "name": "FAQ Query - Minimum Order",
            "query": "berapa minimum pembelian?",
            "expected": "Should retrieve FAQ about minimum order"
        },
    ]

    # Run each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        console.print(f"\n[bold blue]{'═' * 70}[/bold blue]")
        console.print(f"[bold blue]Test {i}/{len(test_scenarios)}: {scenario['name']}[/bold blue]")
        console.print(f"[dim]Expected: {scenario['expected']}[/dim]")
        console.print(f"[bold blue]{'═' * 70}[/bold blue]")

        # Process query
        response = orchestrator.process_query(scenario['query'])

        # Display response
        console.print("\n[bold green]📝 Final Response:[/bold green]")
        panel = Panel(
            response,
            title="[bold cyan]LLM Response[/bold cyan]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)

        # Pause between scenarios
        if i < len(test_scenarios):
            console.print("\n[dim]Press Enter to continue to next scenario...[/dim]", end="")
            input()

    # Test summary
    console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
    console.print("[bold green]✨ All test scenarios completed! ✨[/bold green]")
    console.print("[bold green]" + "=" * 70 + "[/bold green]")

    # Display order tracking summary
    if orchestrator.order_tracker and len(orchestrator.order_tracker) > 0:
        console.print("\n[bold cyan]📦 Order Tracking Summary[/bold cyan]")
        orchestrator.display_order_summary()

        # Export orders
        console.print("\n[bold cyan]💾 Exporting Order Data[/bold cyan]")
        orchestrator.export_orders("orders_export.json", "json")
        orchestrator.export_orders("orders_export.csv", "csv")

        console.print("\n[yellow]💡 Order data saved to:[/yellow]")
        console.print("   - orders.json (persistent storage)")
        console.print("   - orders_export.json (export)")
        console.print("   - orders_export.csv (export)")

        console.print("\n[yellow]🔌 Integration Example:[/yellow]")
        console.print("[dim]")
        console.print("# Access order data programmatically:")
        console.print("from llm_unified import UnifiedRAGOrchestrator")
        console.print("")
        console.print("orchestrator = UnifiedRAGOrchestrator()")
        console.print("orders = orchestrator.get_order_tracker().export_to_dict_list()")
        console.print("")
        console.print("# Process orders in your system")
        console.print("for order in orders:")
        console.print("    print(f\"Order {order['order_id']}: {order['sku']} x {order['requested_quantity_pcs']} pcs\")")
        console.print("    print(f\"  Warehouse: {order['warehouse_name']}\")")
        console.print("    print(f\"  Status: {order['status']}\")")
        console.print("[/dim]")

    return 0


def main():
    """
    Main execution function for testing unified RAG pipeline.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        return run_test_scenarios()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Test interrupted by user[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal Error:[/bold red] {str(e)}")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)