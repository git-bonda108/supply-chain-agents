"""
Mock Data Generator for Supply Chain Demo
Generates realistic mock data when real APIs are unavailable
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List
import os


class MockDataGenerator:
    """
    Generate realistic mock supply chain data for demos.
    """
    
    def __init__(self, output_dir: str = "data/processed"):
        """Initialize mock data generator."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_supplier_data(self, num_suppliers: int = 50) -> pd.DataFrame:
        """
        Generate supplier performance data.
        
        Args:
            num_suppliers: Number of suppliers to generate
        
        Returns:
            DataFrame with supplier data
        """
        countries = ["China", "Vietnam", "India", "Mexico", "Taiwan", "South Korea", "Japan", "Germany"]
        products = ["Memory Chips", "Cobalt", "Rare Earths", "Semiconductors", "Batteries", "Display Panels"]
        
        data = []
        for i in range(num_suppliers):
            country = random.choice(countries)
            product = random.choice(products)
            
            # Risk factors
            is_high_risk_country = country in ["China", "Russia"]
            reliability_base = 0.7 if is_high_risk_country else 0.85
            
            data.append({
                "supplier_id": f"SUP{i+1:03d}",
                "supplier_name": f"Supplier {i+1}",
                "country": country,
                "region": "Asia" if country in ["China", "Vietnam", "India", "Taiwan", "South Korea", "Japan"] else "Other",
                "product_category": product,
                "reliability_score": np.random.normal(reliability_base, 0.1),
                "on_time_delivery": np.random.normal(0.85, 0.1),
                "quality_score": np.random.normal(0.88, 0.08),
                "cost_score": np.random.normal(0.75, 0.1),
                "geopolitical_risk": 0.8 if is_high_risk_country else 0.3,
                "export_control_status": "RESTRICTED" if is_high_risk_country else "ALLOWED"
            })
        
        df = pd.DataFrame(data)
        # Clamp scores to 0-1 range
        for col in ["reliability_score", "on_time_delivery", "quality_score", "cost_score", "geopolitical_risk"]:
            df[col] = df[col].clip(0, 1)
        
        return df
    
    def generate_demand_data(self, num_products: int = 20, days: int = 365) -> pd.DataFrame:
        """
        Generate historical demand data.
        
        Args:
            num_products: Number of products
            days: Number of days of history
        
        Returns:
            DataFrame with demand data
        """
        products = [f"Product_{i+1}" for i in range(num_products)]
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        
        data = []
        for product in products:
            # Generate trend and seasonality
            base_demand = np.random.uniform(100, 1000)
            trend = np.random.uniform(-0.5, 0.5)
            seasonal_amplitude = np.random.uniform(0.1, 0.3)
            
            for date in dates:
                # Trend
                days_from_start = (date - dates[0]).days
                trend_value = 1 + (trend * days_from_start / days)
                
                # Seasonality (weekly pattern)
                seasonal = 1 + seasonal_amplitude * np.sin(2 * np.pi * date.dayofweek / 7)
                
                # Random noise
                noise = np.random.normal(1, 0.1)
                
                demand = base_demand * trend_value * seasonal * noise
                demand = max(0, demand)  # No negative demand
                
                data.append({
                    "date": date,
                    "product_id": product,
                    "demand": int(demand),
                    "weekday": date.dayofweek,
                    "month": date.month
                })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_inventory_data(self, num_products: int = 20) -> pd.DataFrame:
        """
        Generate current inventory data.
        
        Args:
            num_products: Number of products
        
        Returns:
            DataFrame with inventory data
        """
        products = [f"Product_{i+1}" for i in range(num_products)]
        
        data = []
        for product in products:
            current_stock = np.random.uniform(500, 5000)
            reorder_point = np.random.uniform(200, 1000)
            safety_stock = np.random.uniform(100, 500)
            lead_time_days = np.random.uniform(7, 30)
            
            data.append({
                "product_id": product,
                "current_stock": int(current_stock),
                "reorder_point": int(reorder_point),
                "safety_stock": int(safety_stock),
                "lead_time_days": int(lead_time_days),
                "unit_cost": np.random.uniform(10, 100),
                "holding_cost_rate": np.random.uniform(0.15, 0.25)
            })
        
        return pd.DataFrame(data)
    
    def generate_all_data(self):
        """Generate all mock datasets."""
        print("Generating mock supply chain data...")
        
        # Generate datasets
        supplier_df = self.generate_supplier_data()
        demand_df = self.generate_demand_data()
        inventory_df = self.generate_inventory_data()
        
        # Save to CSV
        supplier_df.to_csv(f"{self.output_dir}/suppliers.csv", index=False)
        demand_df.to_csv(f"{self.output_dir}/demand_history.csv", index=False)
        inventory_df.to_csv(f"{self.output_dir}/inventory.csv", index=False)
        
        print(f"✅ Generated {len(supplier_df)} suppliers")
        print(f"✅ Generated {len(demand_df)} demand records")
        print(f"✅ Generated {len(inventory_df)} inventory records")
        print(f"📁 Data saved to {self.output_dir}/")
        
        return {
            "suppliers": supplier_df,
            "demand": demand_df,
            "inventory": inventory_df
        }


if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.generate_all_data()



