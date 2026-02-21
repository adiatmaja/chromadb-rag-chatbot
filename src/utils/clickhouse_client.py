"""
ClickHouse Client Utility Module.

This module provides utilities for connecting to and fetching data from ClickHouse.
Used primarily for loading FAQ data into the vector database.
"""

import sys
import os
import clickhouse_connect
import pandas as pd
from typing import Optional
from rich.console import Console

# Fix Windows console encoding for Unicode characters
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_PORT,
    CLICKHOUSE_DB_NAME,
    CLICKHOUSE_FAQ_TABLE,
)

console = Console()


class ClickHouseClient:
    """
    Client for interacting with ClickHouse database.

    Attributes:
        client: ClickHouse client instance
        host: ClickHouse server host
        port: ClickHouse server port
        database: ClickHouse database name
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, database: Optional[str] = None):
        """
        Initialize ClickHouse client.

        Args:
            host: ClickHouse server host (uses config if not provided)
            port: ClickHouse server port (uses config if not provided)
            database: ClickHouse database name (uses config if not provided)

        Raises:
            ValueError: If credentials are not configured
        """
        self.host = host or CLICKHOUSE_HOST
        self.port = port or CLICKHOUSE_PORT
        self.database = database or CLICKHOUSE_DB_NAME
        self.client = None

        if not self.host or not self.port or not self.database:
            raise ValueError(
                "ClickHouse credentials not configured. "
                "Please set CLICKHOUSE_HOST, CLICKHOUSE_PORT, and CLICKHOUSE_DB_NAME in .env file"
            )

    def connect(self):
        """
        Establish connection to ClickHouse.

        Returns:
            ClickHouseClient: Self for method chaining

        Raises:
            Exception: If connection fails
        """
        try:
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=int(self.port),
                database=self.database
            )

            # Test connection
            self.client.query("SELECT 1")

            console.print(f"[green]✅ Connected to ClickHouse at {self.host}:{self.port}[/green]")
            console.print(f"[cyan]Database: {self.database}[/cyan]")

            return self

        except Exception as e:
            console.print(f"[bold red]❌ Failed to connect to ClickHouse: {e}[/bold red]")
            raise

    def fetch_faq_data(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch FAQ data from ClickHouse.

        Args:
            table_name: Table name (uses config if not provided)

        Returns:
            pandas.DataFrame: DataFrame containing FAQ data

        Raises:
            Exception: If query fails or client not connected
        """
        if not self.client:
            raise Exception("Client not connected. Call connect() first.")

        table = table_name or CLICKHOUSE_FAQ_TABLE

        console.print(f"\n[bold cyan]📥 Fetching FAQ data from:[/bold cyan] {table}")

        try:
            query = f"""
                SELECT
                    id,
                    question,
                    answer,
                    created_at,
                    updated_at,
                    language
                FROM {table}
                ORDER BY id
            """

            # Use query_df to get DataFrame directly with proper column names
            df = self.client.query_df(query)

            console.print(f"[green]✅ Fetched {len(df)} FAQ entries[/green]")
            console.print(f"[dim]Columns: {list(df.columns)}[/dim]")

            return df

        except Exception as e:
            console.print(f"[bold red]❌ Error fetching FAQ data: {e}[/bold red]")
            raise

    def close(self):
        """Close the ClickHouse connection."""
        if self.client:
            self.client.close()
            console.print("[dim]ClickHouse connection closed[/dim]")


def get_faq_data_from_clickhouse() -> pd.DataFrame:
    """
    Convenience function to fetch FAQ data from ClickHouse.

    Returns:
        pandas.DataFrame: FAQ data

    Raises:
        ValueError: If ClickHouse credentials not configured
        Exception: If connection or query fails
    """
    client = ClickHouseClient()
    client.connect()

    try:
        df = client.fetch_faq_data()
        return df
    finally:
        client.close()
