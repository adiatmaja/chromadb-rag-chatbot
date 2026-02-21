"""
Unified Search Agent Module.

This module provides a unified search interface that queries product,
FAQ, and intent collections in ChromaDB. It intelligently determines
which type of content is most relevant to the user's query.

The system supports:
- Product searches (SKU, names, colloquial terms)
- FAQ searches (questions, answers)
- Intent classification (user intent detection)
- Automatic relevance scoring
- Multi-collection querying

Usage:
    python -m src.core.retriever

    Or import as a module:
    from src.core.retriever import UnifiedRetriever
"""

import sys
import os

# Fix Windows console encoding for Unicode characters
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Disable ChromaDB telemetry to suppress warnings
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import chromadb
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

# Import configuration
from src.config import (
    VECTOR_DB_PATH,
    EMBEDDING_MODEL_NAME,
    COLLECTION_NAME,
    RETRIEVAL_TOP_K,
)

# FAQ Configuration
FAQ_COLLECTION_NAME = "faq_collection"
"""Name of the FAQ collection in ChromaDB."""

# Intent Configuration
INTENT_COLLECTION_NAME = "intent_collection"
"""Name of the intent collection in ChromaDB."""

# Initialize rich console for formatted output
console = Console()


class ContentType(Enum):
    """
    Enumeration of content types that can be retrieved.

    Attributes:
        PRODUCT: Product information
        FAQ: Frequently Asked Questions
        INTENT: User intent classification
        UNKNOWN: Unable to determine content type
    """
    PRODUCT = "product"
    FAQ = "faq"
    INTENT = "intent"
    UNKNOWN = "unknown"


class SearchResult:
    """
    Container for unified search results.

    Attributes:
        content_type (ContentType): Type of content retrieved
        metadata (dict): Content metadata
        distance (float): Similarity distance (lower is better)
        relevance_score (float): Normalized relevance score (0-1, higher is better)
    """

    def __init__(
            self,
            content_type: ContentType,
            metadata: Dict[str, Any],
            distance: float
    ):
        """
        Initializes a search result.

        Args:
            content_type (ContentType): Type of content
            metadata (dict): Content metadata
            distance (float): Similarity distance
        """
        self.content_type = content_type
        self.metadata = metadata
        self.distance = distance
        self.relevance_score = max(0.0, 1.0 - distance)

    def __repr__(self):
        return f"SearchResult(type={self.content_type}, score={self.relevance_score:.4f})"


class UnifiedRetriever:
    """
    Unified retrieval system for products, FAQs, and intents.

    This class provides a single interface to search across multiple
    content types and automatically determine the most relevant results.

    Attributes:
        embedding_model (SentenceTransformer): Model for encoding queries
        client (chromadb.PersistentClient): ChromaDB client instance
        product_collection (chromadb.Collection): Product collection
        faq_collection (chromadb.Collection): FAQ collection
        intent_collection (chromadb.Collection): Intent collection
        has_products (bool): Whether product collection is available
        has_faqs (bool): Whether FAQ collection is available
        has_intents (bool): Whether intent collection is available
    """

    def __init__(self):
        """
        Initializes the unified retriever with all collections.

        Raises:
            FileNotFoundError: If ChromaDB database doesn't exist
            ValueError: If no collections exist
        """
        console.print("\n[bold cyan]🚀 Initializing Unified Retrieval System...[/bold cyan]")

        # Load embedding model
        console.print(f"[cyan]Loading embedding model: {EMBEDDING_MODEL_NAME}[/cyan]")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Connect to ChromaDB
        console.print(f"[cyan]Connecting to database: {VECTOR_DB_PATH}[/cyan]")
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

        # Try to load product collection
        self.has_products = False
        self.product_collection = None
        try:
            self.product_collection = self.client.get_collection(name=COLLECTION_NAME)
            product_count = self.product_collection.count()
            console.print(f"[green]✅ Product collection loaded: {product_count} products[/green]")
            self.has_products = True
        except ValueError:
            console.print(f"[yellow]⚠️  Product collection '{COLLECTION_NAME}' not found[/yellow]")

        # Try to load FAQ collection
        self.has_faqs = False
        self.faq_collection = None
        try:
            self.faq_collection = self.client.get_collection(name=FAQ_COLLECTION_NAME)
            faq_count = self.faq_collection.count()
            console.print(f"[green]✅ FAQ collection loaded: {faq_count} FAQs[/green]")
            self.has_faqs = True
        except ValueError:
            console.print(f"[yellow]⚠️  FAQ collection '{FAQ_COLLECTION_NAME}' not found[/yellow]")

        # Try to load Intent collection
        self.has_intents = False
        self.intent_collection = None
        try:
            self.intent_collection = self.client.get_collection(name=INTENT_COLLECTION_NAME)
            intent_count = self.intent_collection.count()
            console.print(f"[green]✅ Intent collection loaded: {intent_count} intents[/green]")
            self.has_intents = True
        except ValueError:
            console.print(f"[yellow]⚠️  Intent collection '{INTENT_COLLECTION_NAME}' not found[/yellow]")

        # Ensure at least one collection is available
        if not self.has_products and not self.has_faqs and not self.has_intents:
            raise ValueError(
                "No collections found! Please run:\n"
                "  - python index_data.py (for products)\n"
                "  - python index_faq.py (for FAQs)\n"
                "  - python index_intent.py (for intents)"
            )

        console.print("[green]✅ Unified Retriever ready![/green]")

    def search(
            self,
            query: str,
            top_k: int = None,
            search_products: bool = True,
            search_faqs: bool = True,
            search_intents: bool = True
    ) -> Optional[SearchResult]:
        """
        Performs unified search across enabled collections.

        Args:
            query (str): User's search query
            top_k (int, optional): Number of results per collection
            search_products (bool): Whether to search product collection
            search_faqs (bool): Whether to search FAQ collection
            search_intents (bool): Whether to search intent collection

        Returns:
            SearchResult or None: Best matching result across all collections

        Note:
            The system automatically selects the most relevant result
            based on similarity scores across all collections.
        """
        if top_k is None:
            top_k = RETRIEVAL_TOP_K

        console.print(f"\n[bold yellow]🔍 Search Query:[/bold yellow] {query}")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()

        # Collect results from all collections
        all_results = []

        # Search products
        if search_products and self.has_products:
            product_results = self._search_collection(
                self.product_collection,
                query_embedding,
                ContentType.PRODUCT,
                top_k
            )
            all_results.extend(product_results)

        # Search FAQs
        if search_faqs and self.has_faqs:
            faq_results = self._search_collection(
                self.faq_collection,
                query_embedding,
                ContentType.FAQ,
                top_k
            )
            all_results.extend(faq_results)

        # Search Intents
        if search_intents and self.has_intents:
            intent_results = self._search_collection(
                self.intent_collection,
                query_embedding,
                ContentType.INTENT,
                top_k
            )
            all_results.extend(intent_results)

        # Return best result
        if not all_results:
            console.print("[bold red]❌ No relevant content found[/bold red]")
            return None

        # Sort by relevance and get best
        best_result = max(all_results, key=lambda r: r.relevance_score)

        self._display_result(best_result, len(all_results))

        return best_result

    def search_all(
            self,
            query: str,
            top_k: int = None,
            search_products: bool = True,
            search_faqs: bool = True,
            search_intents: bool = True
    ) -> List[SearchResult]:
        """
        Performs search and returns all results ranked by relevance.

        Args:
            query (str): User's search query
            top_k (int, optional): Number of results per collection
            search_products (bool): Whether to search product collection
            search_faqs (bool): Whether to search FAQ collection
            search_intents (bool): Whether to search intent collection

        Returns:
            List[SearchResult]: All results sorted by relevance score
        """
        if top_k is None:
            top_k = RETRIEVAL_TOP_K

        console.print(f"\n[bold yellow]🔍 Search Query (All Results):[/bold yellow] {query}")

        query_embedding = self.embedding_model.encode([query]).tolist()
        all_results = []

        # Search products
        if search_products and self.has_products:
            product_results = self._search_collection(
                self.product_collection,
                query_embedding,
                ContentType.PRODUCT,
                top_k
            )
            all_results.extend(product_results)

        # Search FAQs
        if search_faqs and self.has_faqs:
            faq_results = self._search_collection(
                self.faq_collection,
                query_embedding,
                ContentType.FAQ,
                top_k
            )
            all_results.extend(faq_results)

        # Search Intents
        if search_intents and self.has_intents:
            intent_results = self._search_collection(
                self.intent_collection,
                query_embedding,
                ContentType.INTENT,
                top_k
            )
            all_results.extend(intent_results)

        # Sort by relevance
        all_results.sort(key=lambda r: r.relevance_score, reverse=True)

        self._display_all_results(all_results)

        return all_results

    def get_product_candidates(
            self,
            query: str,
            n: int = 3
    ) -> List[SearchResult]:
        """
        Returns top N product candidates for a query.

        Used by the orchestrator to provide multiple candidates to the LLM
        for reranking, improving precision when products are semantically similar.

        Args:
            query (str): User's search query
            n (int): Number of candidates to return

        Returns:
            List[SearchResult]: Top N products sorted by relevance score
        """
        if not self.has_products:
            return []

        count = self.product_collection.count()
        if count == 0:
            return []

        query_embedding = self.embedding_model.encode([query]).tolist()
        candidates = self._search_collection(
            self.product_collection,
            query_embedding,
            ContentType.PRODUCT,
            min(n, count)
        )
        candidates.sort(key=lambda r: r.relevance_score, reverse=True)
        return candidates

    def _search_collection(
            self,
            collection: chromadb.Collection,
            query_embedding: List[float],
            content_type: ContentType,
            top_k: int
    ) -> List[SearchResult]:
        """
        Searches a specific collection and returns results.

        Args:
            collection (chromadb.Collection): Collection to search
            query_embedding (List[float]): Query embedding vector
            content_type (ContentType): Type of content in collection
            top_k (int): Number of results to retrieve

        Returns:
            List[SearchResult]: Search results from this collection
        """
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=['metadatas', 'documents', 'distances']
        )

        search_results = []

        if results and results['metadatas'] and results['metadatas'][0]:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                search_results.append(
                    SearchResult(content_type, metadata, distance)
                )

        return search_results

    def _display_result(self, result: SearchResult, total_searched: int):
        """
        Displays the best search result in formatted output.

        Args:
            result (SearchResult): The best search result
            total_searched (int): Total number of results searched
        """
        console.print(f"\n[bold green]✅ Best Match Found[/bold green] [dim](from {total_searched} results)[/dim]")

        # Create table for structured display
        table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Content Type", result.content_type.value.upper())
        table.add_row("Relevance Score", f"{result.relevance_score:.4f}")

        if result.content_type == ContentType.PRODUCT:
            table.add_row("SKU", result.metadata.get('sku', 'N/A'))
            table.add_row("Product Name", result.metadata.get('official_name', 'N/A'))
            table.add_row("Pack Size", result.metadata.get('pack_size_desc', 'N/A'))
            table.add_row("Aliases", result.metadata.get('colloquial_names', 'N/A'))

        elif result.content_type == ContentType.FAQ:
            table.add_row("FAQ ID", str(result.metadata.get('id', 'N/A')))
            table.add_row("Question", result.metadata.get('question', 'N/A'))
            answer = result.metadata.get('answer', 'N/A')
            # Truncate long answers
            if len(answer) > 200:
                answer = answer[:200] + "..."
            table.add_row("Answer", answer)

        elif result.content_type == ContentType.INTENT:
            table.add_row("Intent Name", result.metadata.get('intent_name', 'N/A'))
            table.add_row("Description", result.metadata.get('description', 'N/A'))
            # Show some query variations if available
            if 'query_variations' in result.metadata and result.metadata['query_variations']:
                variations = result.metadata['query_variations'].split(';')[:3]  # Show first 3
                table.add_row("Example Queries", ' | '.join(variations))

        console.print(table)
        console.print("\n[dim]💡 This data will be used as context for LLM processing[/dim]")

    def _display_all_results(self, results: List[SearchResult]):
        """
        Displays all search results in formatted output.

        Args:
            results (List[SearchResult]): All search results
        """
        console.print(f"\n[bold green]✅ Found {len(results)} Results[/bold green]")

        for i, result in enumerate(results, 1):
            console.print(f"\n[bold cyan]Result {i}:[/bold cyan]")

            table = Table(show_header=False, border_style="dim")
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Value", style="white")

            table.add_row("Type", result.content_type.value.upper())
            table.add_row("Score", f"{result.relevance_score:.4f}")

            if result.content_type == ContentType.PRODUCT:
                table.add_row("SKU", result.metadata.get('sku', 'N/A'))
                table.add_row("Product", result.metadata.get('official_name', 'N/A'))
            elif result.content_type == ContentType.FAQ:
                table.add_row("Question", result.metadata.get('question', 'N/A'))
            elif result.content_type == ContentType.INTENT:
                table.add_row("Intent", result.metadata.get('intent_name', 'N/A'))
                table.add_row("Description", result.metadata.get('description', 'N/A')[:80] + '...' if len(result.metadata.get('description', '')) > 80 else result.metadata.get('description', 'N/A'))

            console.print(table)


def run_test_scenarios():
    """
    Runs test scenarios demonstrating unified search capabilities.

    Test cases include:
    - Product searches
    - FAQ searches
    - Ambiguous queries
    - Multi-result searches
    """
    console.print("\n[bold magenta]" + "=" * 70 + "[/bold magenta]")
    console.print("[bold magenta]    Unified Search System - Test Suite    [/bold magenta]")
    console.print("[bold magenta]" + "=" * 70 + "[/bold magenta]")

    # Initialize retriever
    try:
        retriever = UnifiedRetriever()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize retriever: {e}[/bold red]")
        return 1

    # Define test scenarios
    test_scenarios = [
        {
            "name": "Product Search - Colloquial Name",
            "query": "indomie kuning",
            "description": "Should find product information"
        },
        {
            "name": "FAQ Search - Registration",
            "query": "bagaimana cara mendaftar",
            "description": "Should find FAQ about registration"
        },
        {
            "name": "FAQ Search - Payment Methods",
            "query": "metode pembayaran apa saja yang tersedia",
            "description": "Should find FAQ about payment"
        },
        {
            "name": "Product Search - Specific Item",
            "query": "sabun lifebuoy merah",
            "description": "Should find specific product"
        },
        {
            "name": "FAQ Search - Order Tracking",
            "query": "cara tracking pesanan",
            "description": "Should find FAQ about order tracking"
        },
        {
            "name": "Ambiguous Query",
            "query": "diskon",
            "description": "Could match FAQ about discounts or products"
        },
    ]

    # Run each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        console.print(f"\n[bold blue]{'═' * 70}[/bold blue]")
        console.print(f"[bold blue]Test {i}/{len(test_scenarios)}: {scenario['name']}[/bold blue]")
        console.print(f"[dim]Expected: {scenario['description']}[/dim]")
        console.print(f"[bold blue]{'═' * 70}[/bold blue]")

        # Perform search
        result = retriever.search(scenario['query'])

        # Pause between scenarios
        if i < len(test_scenarios):
            console.print("\n[dim]Press Enter to continue to next test...[/dim]", end="")
            input()

    # Test summary
    console.print("\n[bold green]" + "=" * 70 + "[/bold green]")
    console.print("[bold green]✨ All test scenarios completed! ✨[/bold green]")
    console.print("[bold green]" + "=" * 70 + "[/bold green]")
    console.print("\n[yellow]💡 Next Step:[/yellow] Integrate with LLM using 'python llm_unified.py'")

    return 0


def main():
    """
    Main execution function for testing unified search.

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