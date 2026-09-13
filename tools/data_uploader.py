"""
Data Upload and Preprocessing Module
Handles user-uploaded datasets with validation and preprocessing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataUploader:
    """Handle data upload, validation, and preprocessing."""
    
    def __init__(self, upload_dir: str = "data/uploads", processed_dir: str = "data/processed"):
        """
        Initialize data uploader.
        
        Args:
            upload_dir: Directory for uploaded files
            processed_dir: Directory for processed files
        """
        self.upload_dir = upload_dir
        self.processed_dir = processed_dir
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
    
    def validate_supplier_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate supplier data structure.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_columns = ['supplier_id', 'supplier_name', 'country']
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if len(errors) == 0:
            # Check for duplicates
            if df['supplier_id'].duplicated().any():
                errors.append("Duplicate supplier_id found")
            
            # Check data types
            if not pd.api.types.is_string_dtype(df['supplier_id']):
                errors.append("supplier_id should be string")
        
        return len(errors) == 0, errors
    
    def validate_inventory_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate inventory data structure.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_columns = ['product_id', 'current_stock']
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if len(errors) == 0:
            # Check for duplicates
            if df['product_id'].duplicated().any():
                errors.append("Duplicate product_id found")
            
            # Check numeric columns
            if 'current_stock' in df.columns:
                if not pd.api.types.is_numeric_dtype(df['current_stock']):
                    errors.append("current_stock should be numeric")
                if (df['current_stock'] < 0).any():
                    errors.append("current_stock cannot be negative")
        
        return len(errors) == 0, errors
    
    def validate_demand_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate demand data structure.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_columns = ['date', 'product_id', 'demand']
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if len(errors) == 0:
            # Check date column
            if 'date' in df.columns:
                try:
                    pd.to_datetime(df['date'])
                except:
                    errors.append("date column must be parseable as datetime")
            
            # Check demand column
            if 'demand' in df.columns:
                if not pd.api.types.is_numeric_dtype(df['demand']):
                    errors.append("demand should be numeric")
                if (df['demand'] < 0).any():
                    errors.append("demand cannot be negative")
        
        return len(errors) == 0, errors
    
    def preprocess_supplier_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess supplier data.
        
        Args:
            df: Raw supplier DataFrame
        
        Returns:
            Processed DataFrame
        """
        df = df.copy()
        
        # Fill missing values
        if 'reliability_score' not in df.columns:
            df['reliability_score'] = 0.7  # Default
        df['reliability_score'] = df['reliability_score'].fillna(0.7)
        df['reliability_score'] = df['reliability_score'].clip(0, 1)
        
        if 'on_time_delivery' not in df.columns:
            df['on_time_delivery'] = 0.85
        df['on_time_delivery'] = df['on_time_delivery'].fillna(0.85).clip(0, 1)
        
        if 'quality_score' not in df.columns:
            df['quality_score'] = 0.88
        df['quality_score'] = df['quality_score'].fillna(0.88).clip(0, 1)
        
        if 'cost_score' not in df.columns:
            df['cost_score'] = 0.75
        df['cost_score'] = df['cost_score'].fillna(0.75).clip(0, 1)
        
        # Add geopolitical risk if not present
        if 'geopolitical_risk' not in df.columns:
            high_risk_countries = ['China', 'Russia', 'North Korea']
            df['geopolitical_risk'] = df['country'].apply(
                lambda x: 0.8 if x in high_risk_countries else 0.3
            )
        
        # Add export control status
        if 'export_control_status' not in df.columns:
            high_risk_countries = ['China', 'Russia']
            df['export_control_status'] = df['country'].apply(
                lambda x: 'RESTRICTED' if x in high_risk_countries else 'ALLOWED'
            )
        
        # Add region if not present
        if 'region' not in df.columns:
            asia_countries = ['China', 'Vietnam', 'India', 'Taiwan', 'South Korea', 'Japan']
            df['region'] = df['country'].apply(
                lambda x: 'Asia' if x in asia_countries else 'Other'
            )
        
        # Add product category if not present
        if 'product_category' not in df.columns:
            df['product_category'] = 'General'
        
        return df
    
    def preprocess_inventory_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess inventory data.
        
        Args:
            df: Raw inventory DataFrame
        
        Returns:
            Processed DataFrame
        """
        df = df.copy()
        
        # Ensure numeric columns
        numeric_cols = ['current_stock', 'reorder_point', 'safety_stock', 'lead_time_days', 'unit_cost']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)
        
        # Add missing columns with defaults
        if 'reorder_point' not in df.columns:
            df['reorder_point'] = df['current_stock'] * 0.3
        
        if 'safety_stock' not in df.columns:
            df['safety_stock'] = df['current_stock'] * 0.2
        
        if 'lead_time_days' not in df.columns:
            df['lead_time_days'] = 14  # Default 2 weeks
        
        if 'unit_cost' not in df.columns:
            df['unit_cost'] = 50  # Default
        
        if 'holding_cost_rate' not in df.columns:
            df['holding_cost_rate'] = 0.20  # Default 20%
        
        return df
    
    def preprocess_demand_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess demand data.
        
        Args:
            df: Raw demand DataFrame
        
        Returns:
            Processed DataFrame
        """
        df = df.copy()
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Ensure demand is numeric
        if 'demand' in df.columns:
            df['demand'] = pd.to_numeric(df['demand'], errors='coerce')
            df['demand'] = df['demand'].fillna(0)
            df['demand'] = df['demand'].clip(lower=0)
        
        # Add derived features
        if 'date' in df.columns:
            df['weekday'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
        
        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        return df
    
    def save_uploaded_data(self, df: pd.DataFrame, data_type: str, filename: str) -> str:
        """
        Save uploaded data.
        
        Args:
            df: DataFrame to save
            data_type: Type of data (suppliers, inventory, demand)
            filename: Original filename
        
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{data_type}_{timestamp}_{filename}"
        filepath = os.path.join(self.upload_dir, safe_filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def save_processed_data(self, df: pd.DataFrame, data_type: str) -> str:
        """
        Save processed data.
        
        Args:
            df: Processed DataFrame
            data_type: Type of data (suppliers, inventory, demand)
        
        Returns:
            Path to saved file
        """
        filepath = os.path.join(self.processed_dir, f"{data_type}.csv")
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed {data_type} data to {filepath}")
        return filepath
    
    def process_upload(self, file, data_type: str) -> Dict:
        """
        Process uploaded file.
        
        Args:
            file: Uploaded file object
            data_type: Type of data (suppliers, inventory, demand)
        
        Returns:
            Dict with processing results
        """
        try:
            # Read file
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return {
                    "success": False,
                    "error": "Unsupported file format. Please upload CSV or Excel file."
                }
            
            # Validate
            if data_type == "suppliers":
                is_valid, errors = self.validate_supplier_data(df)
            elif data_type == "inventory":
                is_valid, errors = self.validate_inventory_data(df)
            elif data_type == "demand":
                is_valid, errors = self.validate_demand_data(df)
            else:
                return {
                    "success": False,
                    "error": f"Unknown data type: {data_type}"
                }
            
            if not is_valid:
                return {
                    "success": False,
                    "error": "Validation failed",
                    "errors": errors
                }
            
            # Preprocess
            if data_type == "suppliers":
                df_processed = self.preprocess_supplier_data(df)
            elif data_type == "inventory":
                df_processed = self.preprocess_inventory_data(df)
            elif data_type == "demand":
                df_processed = self.preprocess_demand_data(df)
            
            # Save
            upload_path = self.save_uploaded_data(df, data_type, file.name)
            processed_path = self.save_processed_data(df_processed, data_type)
            
            return {
                "success": True,
                "rows": len(df_processed),
                "columns": list(df_processed.columns),
                "upload_path": upload_path,
                "processed_path": processed_path,
                "preview": df_processed.head(10).to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error processing upload: {e}")
            return {
                "success": False,
                "error": str(e)
            }



