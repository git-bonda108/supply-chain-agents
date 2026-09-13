"""
Data Loader for Supply Chain Datasets
"""

import pandas as pd
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load and manage supply chain datasets.
    Supports both real Kaggle datasets and mock data.
    """
    
    def __init__(self, data_dir: str = "data/processed"):
        """
        Initialize data loader.
        
        Args:
            data_dir: Directory containing processed data files
        """
        self.data_dir = data_dir
        self._cache: Dict[str, pd.DataFrame] = {}
    
    def load_supplier_data(self, supplier_id: Optional[str] = None) -> pd.DataFrame:
        """
        Load supplier data.
        
        Args:
            supplier_id: Optional supplier ID to filter
        
        Returns:
            DataFrame with supplier data
        """
        cache_key = f"suppliers_{supplier_id or 'all'}"
        
        if cache_key not in self._cache:
            file_path = os.path.join(self.data_dir, "suppliers.csv")
            
            if not os.path.exists(file_path):
                logger.warning(f"Supplier data not found at {file_path}. Using mock data.")
                from .mock_data_generator import MockDataGenerator
                generator = MockDataGenerator(self.data_dir)
                generator.generate_supplier_data().to_csv(file_path, index=False)
            
            df = pd.read_csv(file_path)
            
            if supplier_id:
                df = df[df["supplier_id"] == supplier_id]
            
            self._cache[cache_key] = df
        
        return self._cache[cache_key].copy()
    
    def load_demand_history(
        self,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days_back: int = 365
    ) -> pd.DataFrame:
        """
        Load historical demand data.
        
        Args:
            product_id: Optional product ID to filter
            start_date: Optional start date
            end_date: Optional end date
            days_back: Number of days to look back (if dates not provided)
        
        Returns:
            DataFrame with demand history
        """
        file_path = os.path.join(self.data_dir, "demand_history.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Demand data not found at {file_path}. Using mock data.")
            from .mock_data_generator import MockDataGenerator
            generator = MockDataGenerator(self.data_dir)
            generator.generate_demand_data().to_csv(file_path, index=False)
        
        df = pd.read_csv(file_path)
        df["date"] = pd.to_datetime(df["date"])
        
        # Filter by product
        if product_id:
            df = df[df["product_id"] == product_id]
        
        # Filter by date
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=days_back)
        
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        
        return df.sort_values("date")
    
    def load_inventory_data(self, product_id: Optional[str] = None) -> pd.DataFrame:
        """
        Load current inventory data.
        
        Args:
            product_id: Optional product ID to filter
        
        Returns:
            DataFrame with inventory data
        """
        file_path = os.path.join(self.data_dir, "inventory.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Inventory data not found at {file_path}. Using mock data.")
            from .mock_data_generator import MockDataGenerator
            generator = MockDataGenerator(self.data_dir)
            generator.generate_inventory_data().to_csv(file_path, index=False)
        
        df = pd.read_csv(file_path)
        
        if product_id:
            df = df[df["product_id"] == product_id]
        
        return df
    
    def get_supplier_by_country(self, country: str) -> pd.DataFrame:
        """Get suppliers by country."""
        df = self.load_supplier_data()
        return df[df["country"] == country]
    
    def get_supplier_by_product(self, product: str) -> pd.DataFrame:
        """Get suppliers by product category."""
        df = self.load_supplier_data()
        return df[df["product_category"] == product]
    
    def clear_cache(self):
        """Clear data cache."""
        self._cache.clear()


# Create singleton instance
def get_data_loader() -> DataLoader:
    """Get data loader instance."""
    return DataLoader()



