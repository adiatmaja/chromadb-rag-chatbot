"""
Quick Setup Script for RAG Product Search System.

This script automates the initial setup process, including:
- Dependency verification
- Database initialization
- Configuration validation
- System health checks

Usage:
    python setup.py
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
from rich.panel import Panel
from rich.table import Table

console = Console(legacy_windows=False, force_terminal=True)


def check_python_version():
    """
    Verifies Python version meets minimum requirements.

    Returns:
        bool: True if version is acceptable, False otherwise
    """
    console.print("\n[bold cyan]🔍 Checking Python version...[/bold cyan]")

    version = sys.version_info
    required = (3, 9)

    if version >= required:
        console.print(f"[green]✅ Python {version.major}.{version.minor}.{version.micro} detected[/green]")
        return True
    else:
        console.print(f"[red]❌ Python {required[0]}.{required[1]}+ required, found {version.major}.{version.minor}[/red]")
        return False


def check_file_exists(filepath, description):
    """
    Checks if a required file exists.

    Args:
        filepath (Path): Path to the file
        description (str): Human-readable description of the file

    Returns:
        bool: True if file exists, False otherwise
    """
    if filepath.exists():
        console.print(f"[green]✅ {description} found[/green]")
        return True
    else:
        console.print(f"[red]❌ {description} not found at {filepath}[/red]")
        return False


def install_dependencies():
    """
    Installs required Python packages from requirements.txt.

    Returns:
        bool: True if installation successful, False otherwise
    """
    console.print("\n[bold cyan]📦 Installing dependencies...[/bold cyan]")

    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        console.print("[red]❌ requirements.txt not found[/red]")
        return False

    try:
        console.print("[yellow]⏳ This may take a few minutes on first run...[/yellow]")

        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print("[green]✅ Dependencies installed successfully[/green]")
            return True
        else:
            console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Error during installation: {e}[/red]")
        return False


def validate_configuration():
    """
    Validates configuration settings.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    console.print("\n[bold cyan]⚙️  Validating configuration...[/bold cyan]")

    try:
        from src.config import validate_configuration
        validate_configuration()
        console.print("[green]✅ Configuration validated[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Configuration validation failed: {e}[/red]")
        return False


def run_indexing():
    """
    Runs the indexing script to build the vector database.

    Returns:
        bool: True if indexing successful, False otherwise
    """
    console.print("\n[bold cyan]🗂️  Building vector database...[/bold cyan]")

    try:
        # Run product indexing
        result = subprocess.run(
            [sys.executable, "-m", "scripts.indexing.index_products"],
            capture_output=True,
            cwd=project_root
        )

        if result.returncode == 0:
            console.print("[green]✅ Products indexed successfully[/green]")
            return True
        else:
            console.print(f"[red]❌ Indexing failed with exit code {result.returncode}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Indexing failed: {e}[/red]")
        return False


def test_retrieval():
    """
    Performs a quick test of the retrieval system.

    Returns:
        bool: True if test successful, False otherwise
    """
    console.print("\n[bold cyan]🧪 Testing retrieval system...[/bold cyan]")

    try:
        from src.core.retriever import UnifiedRetriever

        retriever = UnifiedRetriever()
        result = retriever.search("indomie goreng")

        if result:
            console.print("[green]✅ Retrieval test passed[/green]")
            console.print(f"[dim]   Found: {result.metadata.get('official_name', 'N/A')}[/dim]")
            return True
        else:
            console.print("[yellow]⚠️  Retrieval returned no results[/yellow]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Retrieval test failed: {e}[/red]")
        return False


def check_lm_studio():
    """
    Checks if LM Studio is accessible.

    Returns:
        bool: True if LM Studio is running, False otherwise
    """
    console.print("\n[bold cyan]🤖 Checking LM Studio connection...[/bold cyan]")

    try:
        import requests
        from src.config import LLM_BASE_URL

        # Try to connect to LM Studio
        response = requests.get(f"{LLM_BASE_URL.rstrip('/v1')}/v1/models", timeout=5)

        if response.status_code == 200:
            console.print("[green]✅ LM Studio is running and accessible[/green]")
            return True
        else:
            console.print(f"[yellow]⚠️  LM Studio responded with status {response.status_code}[/yellow]")
            return False

    except requests.exceptions.ConnectionError:
        console.print("[yellow]⚠️  LM Studio is not running or not accessible[/yellow]")
        console.print("[dim]Note: LM Studio is optional for retrieval-only usage[/dim]")
        return False
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not check LM Studio: {e}[/yellow]")
        return False


def generate_setup_report(results):
    """
    Generates a comprehensive setup report.

    Args:
        results (dict): Dictionary of setup step results
    """
    console.print("\n[bold magenta]" + "="*70 + "[/bold magenta]")
    console.print("[bold magenta]              Setup Report              [/bold magenta]")
    console.print("[bold magenta]" + "="*70 + "[/bold magenta]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=30)
    table.add_column("Status", width=20)
    table.add_column("Notes", style="dim")

    for component, (status, notes) in results.items():
        status_icon = "✅" if status else "❌"
        status_text = f"{status_icon} {'Pass' if status else 'Fail'}"
        table.add_row(component, status_text, notes)

    console.print(table)

    # Overall status
    all_critical_passed = all(
        results[key][0]
        for key in ["Python Version", "Required Files", "Dependencies", "Configuration", "Vector Database"]
    )

    if all_critical_passed:
        console.print("\n[bold green]✨ Setup completed successfully![/bold green]")
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("  1. Test retrieval: [yellow]python search_agent.py[/yellow]")

        if results["LM Studio"][0]:
            console.print("  2. Test full RAG: [yellow]python llm_processor.py[/yellow]")
        else:
            console.print("  2. Start LM Studio and load a model")
            console.print("  3. Test full RAG: [yellow]python llm_processor.py[/yellow]")
    else:
        console.print("\n[bold red]⚠️  Setup incomplete - please resolve errors above[/bold red]")


def main():
    """
    Main setup orchestration function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    console.print("\n[bold magenta]" + "="*70 + "[/bold magenta]")
    console.print("[bold magenta]   RAG Product Search System - Setup Wizard   [/bold magenta]")
    console.print("[bold magenta]" + "="*70 + "[/bold magenta]")

    results = {}

    # Step 1: Check Python version
    results["Python Version"] = (
        check_python_version(),
        "Python 3.9+ required"
    )

    if not results["Python Version"][0]:
        console.print("\n[red]Setup cannot continue with incompatible Python version[/red]")
        return 1

    # Step 2: Check required files
    required_files_exist = all([
        check_file_exists(Path("src/config.py"), "config.py"),
        check_file_exists(Path("scripts/indexing/index_products.py"), "index_products.py"),
        check_file_exists(Path("src/core/retriever.py"), "retriever.py"),
        check_file_exists(Path("data/product_data.csv"), "data/product_data.csv"),
        check_file_exists(Path("requirements.txt"), "requirements.txt"),
    ])

    results["Required Files"] = (
        required_files_exist,
        "All core files present" if required_files_exist else "Missing files"
    )

    if not required_files_exist:
        console.print("\n[red]Setup cannot continue with missing files[/red]")
        return 1

    # Step 3: Install dependencies
    deps_result = install_dependencies()
    results["Dependencies"] = (
        deps_result,
        "All packages installed" if deps_result else "Installation failed"
    )

    if not deps_result:
        console.print("\n[yellow]⚠️  Continuing with existing packages...[/yellow]")

    # Step 4: Validate configuration
    config_result = validate_configuration()
    results["Configuration"] = (
        config_result,
        "Configuration valid" if config_result else "Configuration errors"
    )

    # Step 5: Build vector database
    if config_result:
        indexing_result = run_indexing()
        results["Vector Database"] = (
            indexing_result,
            "Indexed successfully" if indexing_result else "Indexing failed"
        )
    else:
        results["Vector Database"] = (False, "Skipped due to config errors")

    # Step 6: Test retrieval
    if results["Vector Database"][0]:
        retrieval_result = test_retrieval()
        results["Retrieval System"] = (
            retrieval_result,
            "Working correctly" if retrieval_result else "Test failed"
        )
    else:
        results["Retrieval System"] = (False, "Skipped")

    # Step 7: Check LM Studio (optional)
    lm_studio_result = check_lm_studio()
    results["LM Studio"] = (
        lm_studio_result,
        "Connected" if lm_studio_result else "Not running (optional)"
    )

    # Generate final report
    generate_setup_report(results)

    return 0 if results["Vector Database"][0] else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Setup interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)