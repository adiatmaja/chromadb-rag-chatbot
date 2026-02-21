"""
FAQ Integration Setup Script.

This script automates the setup process for FAQ integration into
the existing RAG Product Search System. It performs:
- File verification
- Dependency checking
- FAQ data validation
- Database indexing
- System testing

Usage:
    python setup_faq.py
"""

import sys
import subprocess
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console(legacy_windows=False, force_terminal=True)


def print_header():
    """
    Displays the setup script header.
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]   FAQ Integration Setup Wizard   [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")


def check_file_exists(filepath, description):
    """
    Checks if a required file exists.

    Args:
        filepath (Path): Path to the file
        description (str): Human-readable description

    Returns:
        bool: True if file exists, False otherwise
    """
    if filepath.exists():
        console.print(f"[green]✅ {description} found[/green]")
        return True
    else:
        console.print(f"[red]❌ {description} not found at {filepath}[/red]")
        return False


def validate_faq_data():
    """
    Validates the FAQ data from ClickHouse.

    Returns:
        bool: True if validation successful, False otherwise
    """
    console.print("\n[bold cyan]📋 Validating FAQ data from ClickHouse...[/bold cyan]")

    try:
        from src.config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DB_NAME
        from src.utils.clickhouse_client import get_faq_data_from_clickhouse

        # Check if credentials are configured
        if not CLICKHOUSE_HOST or not CLICKHOUSE_PORT or not CLICKHOUSE_DB_NAME:
            console.print("[red]❌ ClickHouse credentials not configured[/red]")
            console.print("[yellow]Please configure in .env file:[/yellow]")
            console.print("  - CLICKHOUSE_HOST")
            console.print("  - CLICKHOUSE_PORT")
            console.print("  - CLICKHOUSE_DB_NAME")
            return False

        # Fetch data from ClickHouse
        df = get_faq_data_from_clickhouse()

        # Check required columns
        required_cols = ['id', 'question', 'answer', 'language']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            console.print(f"[red]❌ Missing columns: {missing_cols}[/red]")
            return False

        # Check data quality
        if len(df) == 0:
            console.print("[red]❌ FAQ data is empty[/red]")
            return False

        console.print(f"[green]✅ FAQ data validated: {len(df)} entries from ClickHouse[/green]")

        # Show sample
        console.print("\n[dim]Sample FAQ entries:[/dim]")
        sample_table = Table(show_header=True, header_style="bold")
        sample_table.add_column("ID", width=5)
        sample_table.add_column("Question", width=40)

        for _, row in df.head(3).iterrows():
            question = str(row['question'])[:37] + "..." if len(str(row['question'])) > 40 else str(row['question'])
            sample_table.add_row(str(row['id']), question)

        console.print(sample_table)

        return True

    except Exception as e:
        console.print(f"[red]❌ Error validating FAQ data: {e}[/red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return False


def check_existing_collections():
    """
    Checks status of existing vector database collections.

    Returns:
        tuple: (has_products, has_faqs)
    """
    console.print("\n[bold cyan]🔍 Checking existing collections...[/bold cyan]")

    has_products = False
    has_faqs = False

    try:
        import chromadb
        from src.config import VECTOR_DB_PATH

        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

        # Check product collection
        try:
            prod_collection = client.get_collection(name="fmcg_products")
            prod_count = prod_collection.count()
            console.print(f"[green]✅ Product collection found: {prod_count} products[/green]")
            has_products = True
        except:
            console.print("[yellow]⚠️  Product collection not found[/yellow]")

        # Check FAQ collection
        try:
            faq_collection = client.get_collection(name="faq_collection")
            faq_count = faq_collection.count()
            console.print(f"[green]✅ FAQ collection found: {faq_count} FAQs[/green]")
            has_faqs = True
        except:
            console.print("[yellow]⚠️  FAQ collection not found (will be created)[/yellow]")

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not check collections: {e}[/yellow]")

    return has_products, has_faqs


def run_faq_indexing():
    """
    Runs the FAQ indexing process.

    Returns:
        bool: True if indexing successful, False otherwise
    """
    console.print("\n[bold cyan]🔄 Indexing FAQ data...[/bold cyan]")
    console.print("[yellow]⏳ This may take a minute...[/yellow]")

    try:
        # Run indexing script as subprocess for better isolation
        result = subprocess.run(
            [sys.executable, "-m", "scripts.indexing.index_faq"],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        # Print output for visibility
        if result.stdout:
            print(result.stdout)

        # Check if indexing succeeded
        if result.returncode == 0:
            console.print("[green]✅ FAQ indexing completed successfully[/green]")
            return True
        else:
            console.print(f"[red]❌ Indexing failed with exit code {result.returncode}[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Indexing failed: {e}[/red]")
        return False


def test_unified_search():
    """
    Tests the unified search functionality.

    Returns:
        bool: True if test successful, False otherwise
    """
    console.print("\n[bold cyan]🧪 Testing unified search...[/bold cyan]")

    try:
        from src.core.retriever import UnifiedRetriever, ContentType

        retriever = UnifiedRetriever()

        # Test FAQ query
        console.print("[dim]Testing FAQ query: 'bagaimana cara mendaftar'[/dim]")
        faq_result = retriever.search("bagaimana cara mendaftar")

        if faq_result and faq_result.content_type == ContentType.FAQ:
            console.print("[green]✅ FAQ search test passed[/green]")
        else:
            console.print("[yellow]⚠️  FAQ search returned unexpected result[/yellow]")

        # Test product query
        console.print("[dim]Testing product query: 'indomie goreng'[/dim]")
        prod_result = retriever.search("indomie goreng")

        if prod_result and prod_result.content_type == ContentType.PRODUCT:
            console.print("[green]✅ Product search test passed[/green]")
        else:
            console.print("[yellow]⚠️  Product search returned unexpected result[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]❌ Search test failed: {e}[/red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return False


def generate_setup_report(results):
    """
    Generates a comprehensive setup report.

    Args:
        results (dict): Dictionary of setup step results
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]              Setup Report              [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=30)
    table.add_column("Status", width=15)
    table.add_column("Notes", style="dim")

    for component, (status, notes) in results.items():
        status_icon = "✅" if status else "❌"
        status_text = f"{status_icon} {'Pass' if status else 'Fail'}"
        table.add_row(component, status_text, notes)

    console.print(table)

    # Overall status
    all_critical_passed = all(
        results[key][0]
        for key in ["Required Files", "FAQ Data", "FAQ Indexing"]
    )

    if all_critical_passed:
        console.print("\n[bold green]✨ FAQ Integration completed successfully![/bold green]")

        console.print("\n[bold cyan]🎯 What You Can Do Now:[/bold cyan]")

        panel_content = """
1. Test Unified Retriever (Python):
   from src.core.retriever import UnifiedRetriever
   retriever = UnifiedRetriever()
   result = retriever.search("bagaimana cara mendaftar?")

2. Test Full RAG System (Python):
   from src.core.orchestrator import UnifiedRAGOrchestrator
   orchestrator = UnifiedRAGOrchestrator()
   response = orchestrator.process_query("bagaimana cara mendaftar?")

3. Run Order Tracking Demo:
   python -m examples.order_tracking_demo

4. Try These Sample Queries:
   - "Mau beli 3 dus Indomie kuning" (Product + Inventory)
   - "Bagaimana cara mendaftar?" (FAQ)
   - "Apa saja metode pembayaran?" (FAQ)
   - "tolong carikan sabun lifebuoy" (Product Info)
"""
        console.print(Panel(
            panel_content,
            title="[bold green]Next Steps[/bold green]",
            border_style="green"
        ))

        console.print("\n[yellow]📚 For detailed information:[/yellow]")
        console.print("   - Config: .env file for settings")
        console.print("   - Code: src/core/ directory")

    else:
        console.print("\n[bold red]⚠️  Setup incomplete - please resolve errors above[/bold red]")

        if not results["FAQ Data"][0]:
            console.print("\n[yellow]💡 Fix FAQ Data:[/yellow]")
            console.print("   - Configure ClickHouse credentials in .env")
            console.print("   - Ensure CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DB_NAME are set")
            console.print("   - Verify ClickHouse table exists: your_database.faq")
            console.print("   - Check ClickHouse connectivity")

        if not results["FAQ Indexing"][0]:
            console.print("\n[yellow]💡 Fix Indexing:[/yellow]")
            console.print("   - Run: python scripts/indexing/index_faq.py")
            console.print("   - Check error messages")
            console.print("   - Verify ChromaDB installation")
            console.print("   - Ensure ClickHouse is accessible")


def main():
    """
    Main setup orchestration function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print_header()

    console.print("\n[cyan]This wizard will help you integrate FAQs into your RAG system.[/cyan]")
    console.print("[dim]Press Ctrl+C at any time to cancel.[/dim]\n")

    results = {}

    # Step 1: Check required files
    console.print("\n[bold cyan]📁 Step 1: Checking Required Files[/bold cyan]")

    required_files_exist = all([
        check_file_exists(Path("scripts/indexing/index_faq.py"), "FAQ indexing script"),
        check_file_exists(Path("src/config.py"), "Configuration file"),
        check_file_exists(Path("src/utils/clickhouse_client.py"), "ClickHouse client utility"),
        check_file_exists(Path("src/core/retriever.py"), "Unified retriever"),
    ])

    results["Required Files"] = (
        required_files_exist,
        "All files present" if required_files_exist else "Missing files"
    )

    if not required_files_exist:
        console.print("\n[red]Cannot continue without required files[/red]")
        console.print("[yellow]Please ensure all FAQ integration files are in place.[/yellow]")
        return 1

    # Step 2: Validate FAQ data
    console.print("\n[bold cyan]📋 Step 2: Validating FAQ Data[/bold cyan]")
    faq_valid = validate_faq_data()

    results["FAQ Data"] = (
        faq_valid,
        "Data validated" if faq_valid else "Validation failed"
    )

    if not faq_valid:
        console.print("\n[red]Cannot continue with invalid FAQ data[/red]")
        return 1

    # Step 3: Check existing collections
    console.print("\n[bold cyan]🗂️  Step 3: Checking Existing Collections[/bold cyan]")
    has_products, has_faqs = check_existing_collections()

    results["Existing Collections"] = (
        True,
        f"Products: {'Yes' if has_products else 'No'}, FAQs: {'Yes' if has_faqs else 'No'}"
    )

    if not has_products:
        console.print("\n[yellow]⚠️  Recommendation: Run 'python index_data.py' first[/yellow]")
        console.print("[dim]The system works with FAQs only, but products are recommended.[/dim]")

    # Step 4: Index FAQ data
    if has_faqs:
        console.print("\n[yellow]FAQ collection already exists.[/yellow]")
        user_input = input("Do you want to re-index? (y/N): ").strip().lower()

        if user_input == 'y':
            indexing_result = run_faq_indexing()
        else:
            console.print("[cyan]Skipping re-indexing[/cyan]")
            indexing_result = True
    else:
        indexing_result = run_faq_indexing()

    results["FAQ Indexing"] = (
        indexing_result,
        "Indexed successfully" if indexing_result else "Indexing failed"
    )

    # Step 5: Test unified search
    if indexing_result:
        test_result = test_unified_search()
        results["Unified Search Test"] = (
            test_result,
            "Tests passed" if test_result else "Tests failed"
        )
    else:
        results["Unified Search Test"] = (False, "Skipped due to indexing failure")

    # Generate final report
    generate_setup_report(results)

    return 0 if results["FAQ Indexing"][0] else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Setup cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
        import traceback

        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)