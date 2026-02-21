"""
Inventory Management API Module.

This module provides a FastAPI-based REST API for managing and querying
product inventory information. It serves as the backend for stock checks
in the RAG product search system.

Features:
- Real-time stock availability checks
- Warehouse location tracking
- Quantity validation
- RESTful API endpoints
- Automatic data loading from CSV

Usage:
    Start the API server:
    uvicorn stock_api:app --reload --port 8000

    Or run directly:
    python stock_api.py

API Documentation:
    Once running, visit:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from datetime import datetime

# --- MODIFIED: Added 'Path' for the bug fix ---
from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath, status
from fastapi.responses import JSONResponse
# --- MODIFIED: Updated Pydantic imports for V2 ---
from pydantic import BaseModel, Field, field_validator, ConfigDict
import uvicorn


# ============================================================================
# CONFIGURATION
# ============================================================================

STOCK_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "data/stock_data.csv"
"""Path to the stock inventory CSV file."""

API_VERSION = "1.0.0"
"""Current API version."""

API_TITLE = "Product Inventory Management API"
"""API title for documentation."""

API_DESCRIPTION = """
REST API for managing product inventory in the RAG Product Search System.

This API provides endpoints for:
* Checking stock availability by SKU
* Querying inventory across warehouses
* Validating order quantities
* Retrieving warehouse information

Built with FastAPI for high performance and automatic API documentation.
"""


# ============================================================================
# PYDANTIC MODELS (DATA VALIDATION)
# ============================================================================

class WarehouseInfo(BaseModel):
    """
    Warehouse information model.

    Attributes:
        warehouse_id (str): Unique warehouse identifier
        warehouse_name (str): Human-readable warehouse name
        location (str): Warehouse location/address
        available_quantity (int): Stock quantity available at this warehouse
    """
    warehouse_id: str = Field(..., description="Unique warehouse identifier")
    warehouse_name: str = Field(..., description="Warehouse name")
    location: str = Field(..., description="Warehouse location")
    available_quantity: int = Field(..., ge=0, description="Available stock quantity")


# --- MODIFIED: Updated 'StockInfo' for Pydantic V2 ---
class StockInfo(BaseModel):
    """
    Complete stock information for a product.

    Attributes:
        sku (str): Product SKU identifier
        product_name (str): Official product name
        total_quantity (int): Total available quantity across all warehouses
        reserved_quantity (int): Quantity reserved for pending orders
        available_quantity (int): Quantity available for new orders
        reorder_level (int): Minimum quantity before reorder
        warehouses (List[WarehouseInfo]): Stock distribution across warehouses
        last_updated (str): Timestamp of last inventory update
    """
    sku: str = Field(..., description="Product SKU")
    product_name: str = Field(..., description="Official product name")
    total_quantity: int = Field(..., ge=0, description="Total stock quantity")
    reserved_quantity: int = Field(..., ge=0, description="Reserved quantity")
    available_quantity: int = Field(..., ge=0, description="Available quantity")
    reorder_level: int = Field(..., ge=0, description="Reorder threshold")
    warehouses: List[WarehouseInfo] = Field(default_factory=list, description="Warehouse distribution")
    last_updated: str = Field(..., description="Last update timestamp")

    # Replaced @validator with @field_validator and updated signature
    @field_validator('available_quantity')
    @classmethod
    def validate_available_quantity(cls, value, info):
        """
        Validates that available quantity doesn't exceed total quantity.

        Args:
            value (int): Available quantity to validate
            info (ValidationInfo): Pydantic validation info object

        Returns:
            int: Validated available quantity

        Raises:
            ValueError: If available quantity exceeds total quantity
        """
        # Use info.data to access other fields
        if 'total_quantity' in info.data and value > info.data['total_quantity']:
            raise ValueError('Available quantity cannot exceed total quantity')
        return value


# --- MODIFIED: Updated 'StockCheckRequest' for Pydantic V2 ---
class StockCheckRequest(BaseModel):
    """
    Request model for stock availability checks.

    Attributes:
        sku (str): Product SKU to check
        requested_quantity (int): Quantity requested
        warehouse_id (Optional[str]): Specific warehouse to check (optional)
    """
    sku: str = Field(..., min_length=3, max_length=20, description="Product SKU")
    requested_quantity: int = Field(..., gt=0, description="Requested quantity (must be positive)")
    warehouse_id: Optional[str] = Field(None, description="Specific warehouse ID (optional)")

    # Replaced class Config with model_config and schema_extra with json_schema_extra
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "IR001",
                "requested_quantity": 120,
                "warehouse_id": "WH001"
            }
        }
    )


# --- MODIFIED: Updated 'StockCheckResponse' for Pydantic V2 ---
class StockCheckResponse(BaseModel):
    """
    Response model for stock availability checks.

    Attributes:
        status (str): Status of the request (success/partial/error)
        available (bool): Whether requested quantity is available
        sku (str): Product SKU checked
        requested_quantity (int): Quantity requested
        available_quantity (int): Quantity actually available
        warehouse (Optional[str]): Warehouse where stock is available
        message (str): Human-readable status message
        suggested_alternatives (Optional[List[str]]): Alternative suggestions if unavailable
    """
    status: str = Field(..., description="Request status")
    available: bool = Field(..., description="Stock availability")
    sku: str = Field(..., description="Product SKU")
    requested_quantity: int = Field(..., description="Requested quantity")
    available_quantity: int = Field(..., description="Available quantity")
    warehouse: Optional[str] = Field(None, description="Warehouse with stock")
    message: str = Field(..., description="Status message")
    suggested_alternatives: Optional[List[str]] = Field(None, description="Alternative suggestions")

    # Replaced class Config with model_config and schema_extra with json_schema_extra
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "available": True,
                "sku": "IR001",
                "requested_quantity": 120,
                "available_quantity": 120,
                "warehouse": "Gudang A",
                "message": "Stock available and ready to ship",
                "suggested_alternatives": None
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """
    API health check response.

    Attributes:
        status (str): API status
        version (str): API version
        timestamp (str): Current timestamp
        total_products (int): Number of products in inventory
        total_warehouses (int): Number of warehouses
    """
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    total_products: int = Field(..., description="Total products in inventory")
    total_warehouses: int = Field(..., description="Total warehouses")


# ============================================================================
# INVENTORY MANAGER (BUSINESS LOGIC)
# ============================================================================

class InventoryManager:
    """
    Manages inventory data and business logic.

    Handles loading stock data from CSV, querying inventory,
    and performing stock availability calculations.

    Attributes:
        stock_data (pd.DataFrame): Loaded stock inventory data
        warehouse_data (pd.DataFrame): Warehouse information
    """

    def __init__(self, stock_data_path: Path):
        """
        Initializes the inventory manager and loads stock data.

        Args:
            stock_data_path (Path): Path to stock data CSV file

        Raises:
            FileNotFoundError: If stock data file doesn't exist
            ValueError: If stock data format is invalid
        """
        self.stock_data_path = stock_data_path
        self.stock_data = None
        self.warehouse_data = None
        self._load_stock_data()

    def _load_stock_data(self) -> None:
        """
        Loads and validates stock data from CSV file.

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.stock_data_path.exists():
            raise FileNotFoundError(
                f"Stock data file not found: {self.stock_data_path}. "
                f"Please ensure stock_data.csv exists in the project root."
            )

        try:
            self.stock_data = pd.read_csv(self.stock_data_path)

            # Validate required columns
            required_columns = ['sku', 'product_name', 'warehouse_id', 'warehouse_name',
                              'location', 'quantity', 'reserved_quantity', 'reorder_level']
            missing_columns = [col for col in required_columns if col not in self.stock_data.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns in stock data: {missing_columns}")

            # Group warehouse data
            self.warehouse_data = self.stock_data.groupby('warehouse_id').first()[
                ['warehouse_name', 'location']
            ].reset_index()

        except Exception as e:
            raise ValueError(f"Failed to load stock data: {str(e)}")

    def get_stock_by_sku(self, sku: str) -> Optional[StockInfo]:
        """
        Retrieves complete stock information for a given SKU.

        Args:
            sku (str): Product SKU to query

        Returns:
            StockInfo: Complete stock information if found, None otherwise
        """
        product_stocks = self.stock_data[self.stock_data['sku'] == sku]

        if product_stocks.empty:
            return None

        # Aggregate stock across warehouses
        total_quantity = product_stocks['quantity'].sum()
        total_reserved = product_stocks['reserved_quantity'].sum()
        available_quantity = total_quantity - total_reserved

        # Get warehouse distribution
        warehouses = []
        for _, row in product_stocks.iterrows():
            warehouse_available = row['quantity'] - row['reserved_quantity']
            warehouses.append(WarehouseInfo(
                warehouse_id=row['warehouse_id'],
                warehouse_name=row['warehouse_name'],
                location=row['location'],
                available_quantity=max(0, warehouse_available)
            ))

        return StockInfo(
            sku=sku,
            product_name=product_stocks.iloc[0]['product_name'],
            total_quantity=int(total_quantity),
            reserved_quantity=int(total_reserved),
            available_quantity=max(0, int(available_quantity)),
            reorder_level=int(product_stocks.iloc[0]['reorder_level']),
            warehouses=warehouses,
            last_updated=datetime.now().isoformat()
        )

    def check_availability(
        self,
        sku: str,
        requested_quantity: int,
        warehouse_id: Optional[str] = None
    ) -> StockCheckResponse:
        """
        Checks stock availability for a specific quantity request.

        Args:
            sku (str): Product SKU to check
            requested_quantity (int): Quantity requested
            warehouse_id (Optional[str]): Specific warehouse to check

        Returns:
            StockCheckResponse: Detailed availability information

        Note:
            If warehouse_id is provided, only checks that warehouse.
            Otherwise, checks all warehouses and selects the best option.
        """
        stock_info = self.get_stock_by_sku(sku)

        if not stock_info:
            return StockCheckResponse(
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
            warehouse = next(
                (wh for wh in stock_info.warehouses if wh.warehouse_id == warehouse_id),
                None
            )

            if not warehouse:
                return StockCheckResponse(
                    status="error",
                    available=False,
                    sku=sku,
                    requested_quantity=requested_quantity,
                    available_quantity=0,
                    warehouse=warehouse_id,
                    message=f"Warehouse {warehouse_id} not found or has no stock for this product."
                )

            available_qty = warehouse.available_quantity
            warehouse_name = warehouse.warehouse_name
        else:
            # Check across all warehouses, prioritize warehouse with sufficient stock
            available_qty = stock_info.available_quantity

            # Find warehouse with most stock
            best_warehouse = max(stock_info.warehouses, key=lambda w: w.available_quantity)
            warehouse_name = best_warehouse.warehouse_name

        # Determine availability status
        if available_qty >= requested_quantity:
            return StockCheckResponse(
                status="success",
                available=True,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=available_qty,
                warehouse=warehouse_name,
                message=f"Stok {sku} sebanyak {requested_quantity} pcs tersedia di {warehouse_name}. Silakan lanjutkan pembayaran."
            )
        elif available_qty > 0:
            return StockCheckResponse(
                status="partial",
                available=True,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=available_qty,
                warehouse=warehouse_name,
                message=f"Stok {sku} sejumlah {requested_quantity} pcs tidak tersedia. Maksimal tersedia {available_qty} pcs di {warehouse_name}.",
                suggested_alternatives=[f"Reduce quantity to {available_qty} pcs"]
            )
        else:
            return StockCheckResponse(
                status="error",
                available=False,
                sku=sku,
                requested_quantity=requested_quantity,
                available_quantity=0,
                warehouse=warehouse_name,
                message=f"Stok {sku} habis. Produk sedang dalam proses pengisian ulang.",
                suggested_alternatives=["Check back later", "Contact support for restock information"]
            )

    def get_all_products(self) -> List[str]:
        """
        Returns list of all product SKUs in inventory.

        Returns:
            List[str]: List of unique SKUs
        """
        return self.stock_data['sku'].unique().tolist()

    def get_all_warehouses(self) -> List[Dict[str, str]]:
        """
        Returns list of all warehouses.

        Returns:
            List[dict]: List of warehouse information dictionaries
        """
        return self.warehouse_data.to_dict('records')


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize inventory manager (global instance)
try:
    inventory_manager = InventoryManager(STOCK_DATA_FILE)
except Exception as e:
    print(f"ERROR: Failed to initialize inventory manager: {e}")
    print(f"Please ensure {STOCK_DATA_FILE} exists and is properly formatted.")
    inventory_manager = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get(
    "/",
    response_model=Dict[str, str],
    tags=["General"],
    summary="API Root",
    description="Returns basic API information and available endpoints."
)
async def root():
    """
    Root endpoint providing API overview.

    Returns:
        dict: API information including name, version, and documentation links
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health_check": "/health"
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["General"],
    summary="Health Check",
    description="Checks API health status and returns system information."
)
async def health_check():
    """
    Health check endpoint for monitoring and diagnostics.

    Returns:
        HealthCheckResponse: Current API health status and statistics

    Raises:
        HTTPException: If inventory manager is not initialized
    """
    if not inventory_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory manager not initialized. Check stock_data.csv file."
        )

    return HealthCheckResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=datetime.now().isoformat(),
        total_products=len(inventory_manager.get_all_products()),
        total_warehouses=len(inventory_manager.get_all_warehouses())
    )


# --- MODIFIED: Changed 'Query' to 'Path' to fix the crash ---
@app.get(
    "/api/v1/inventory/{sku}",
    response_model=StockInfo,
    tags=["Inventory"],
    summary="Get Stock Information",
    description="Retrieves complete stock information for a product by SKU."
)
async def get_stock_info(
    sku: str = FastApiPath(..., description="Product SKU to query", min_length=3, max_length=20)
):
    """
    Retrieves detailed stock information for a specific product.

    Args:
        sku (str): Product SKU identifier

    Returns:
        StockInfo: Complete stock information including warehouse distribution

    Raises:
        HTTPException: If SKU is not found in inventory
    """
    if not inventory_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory service unavailable"
        )

    stock_info = inventory_manager.get_stock_by_sku(sku)

    if not stock_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found in inventory"
        )

    return stock_info


@app.post(
    "/api/v1/inventory/check",
    response_model=StockCheckResponse,
    tags=["Inventory"],
    summary="Check Stock Availability",
    description="Checks if requested quantity is available for a product."
)
async def check_stock_availability(request: StockCheckRequest):
    """
    Checks stock availability for a specific quantity request.

    This endpoint is used by the RAG system's LLM to verify
    inventory before confirming orders.

    Args:
        request (StockCheckRequest): Stock check request with SKU and quantity

    Returns:
        StockCheckResponse: Detailed availability information

    Raises:
        HTTPException: If inventory service is unavailable
    """
    if not inventory_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory service unavailable"
        )

    return inventory_manager.check_availability(
        sku=request.sku,
        requested_quantity=request.requested_quantity,
        warehouse_id=request.warehouse_id
    )


@app.get(
    "/api/v1/products",
    response_model=List[str],
    tags=["Products"],
    summary="List All Products",
    description="Returns list of all product SKUs in inventory."
)
async def list_products():
    """
    Lists all product SKUs available in the inventory.

    Returns:
        List[str]: List of unique product SKUs

    Raises:
        HTTPException: If inventory service is unavailable
    """
    if not inventory_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory service unavailable"
        )

    return inventory_manager.get_all_products()


@app.get(
    "/api/v1/warehouses",
    response_model=List[Dict[str, str]],
    tags=["Warehouses"],
    summary="List All Warehouses",
    description="Returns list of all warehouses with their information."
)
async def list_warehouses():
    """
    Lists all warehouses in the inventory system.

    Returns:
        List[dict]: List of warehouse information

    Raises:
        HTTPException: If inventory service is unavailable
    """
    if not inventory_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory service unavailable"
        )

    return inventory_manager.get_all_warehouses()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """
    Handles ValueError exceptions with proper HTTP response.

    Args:
        request: FastAPI request object
        exc: ValueError exception

    Returns:
        JSONResponse: Error response with 400 status code
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    """
    Handles FileNotFoundError exceptions with proper HTTP response.

    Args:
        request: FastAPI request object
        exc: FileNotFoundError exception

    Returns:
        JSONResponse: Error response with 503 status code
    """
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Service unavailable: {str(exc)}"}
    )


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Runs the FastAPI application using Uvicorn server.

    Server Configuration:
    - Host: 0.0.0.0 (accessible from network)
    - Port: 8000
    - Reload: Enabled (auto-restart on code changes)
    """
    print("=" * 70)
    print(f"  {API_TITLE}")
    print(f"  Version: {API_VERSION}")
    print("=" * 70)
    print("\nStarting API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/health")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run(
        "stock_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()