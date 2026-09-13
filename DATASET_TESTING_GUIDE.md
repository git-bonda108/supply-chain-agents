# Dataset Testing Guide - Using Real Supply Chain Data

## 📊 Found Dataset

**File**: `~/Downloads/supply_chain_data.csv`
- **Size**: 20.6 KB
- **Rows**: 100
- **Columns**: 24

### Dataset Structure

The dataset contains:
- **Product Info**: Product type, SKU, Price, Availability
- **Sales Data**: Number of products sold, Revenue generated
- **Inventory**: Stock levels, Lead times, Order quantities
- **Shipping**: Shipping times, Carriers, Shipping costs, Routes
- **Supplier Info**: Supplier name, Location, Lead time
- **Manufacturing**: Production volumes, Manufacturing lead time, Manufacturing costs
- **Quality**: Inspection results, Defect rates
- **Logistics**: Transportation modes, Routes, Costs

---

## 🧪 How to Test with This Dataset

### Step 1: Prepare Data for Upload

The dataset needs to be transformed to match our system's expected format:

#### For Suppliers Data:
```python
# Extract supplier information
suppliers_df = df[['Supplier name', 'Location']].drop_duplicates()
suppliers_df.columns = ['supplier_name', 'country']
suppliers_df['supplier_id'] = 'SUP' + suppliers_df.index.astype(str).str.zfill(3)
```

#### For Inventory Data:
```python
# Extract inventory information
inventory_df = df[['SKU', 'Stock levels', 'Lead times']].copy()
inventory_df.columns = ['product_id', 'current_stock', 'lead_time_days']
inventory_df['reorder_point'] = inventory_df['current_stock'] * 0.3
inventory_df['unit_cost'] = df['Price']
```

#### For Demand Data:
```python
# Create demand history (simulate from sales data)
demand_df = pd.DataFrame({
    'date': pd.date_range(end=datetime.now(), periods=90, freq='D'),
    'product_id': df['SKU'].iloc[0],  # Use first SKU
    'demand': df['Number of products sold'].iloc[0] / 90  # Daily average
})
```

### Step 2: Upload to System

1. **Go to "Data Upload & Analysis" tab**
2. **Select "suppliers"** → Upload suppliers CSV
3. **Select "inventory"** → Upload inventory CSV
4. **Select "demand"** → Upload demand CSV

### Step 3: Test Each Tab

---

## 📋 Test Cases with Real Dataset

### Test Case: Upload Suppliers from Real Dataset

**Steps**:
1. Transform dataset to supplier format
2. Save as CSV
3. Upload in "Data Upload & Analysis" tab
4. Select "suppliers"
5. Upload file
6. Click "Process Suppliers Data"

**Expected Results**:
- ✅ Validates: supplier_id, supplier_name, country
- ✅ Preprocesses: Adds reliability_score, geopolitical_risk
- ✅ Shows: "✅ Successfully processed X rows!"
- ✅ Preview: Shows processed data

**What to Verify**:
- Supplier count matches dataset
- Countries are recognized
- Risk scores assigned (China = high risk, others = low risk)

---

### Test Case: Upload Inventory from Real Dataset

**Steps**:
1. Transform to inventory format
2. Upload as "inventory" type

**Expected Results**:
- ✅ Validates: product_id, current_stock
- ✅ Preprocesses: Adds reorder_point, safety_stock
- ✅ Shows stock value calculation
- ✅ Identifies low stock items

**What to Verify**:
- Product count matches
- Stock levels are correct
- Reorder points calculated

---

### Test Case: Upload Demand from Real Dataset

**Steps**:
1. Create demand history from sales data
2. Upload as "demand" type

**Expected Results**:
- ✅ Validates: date, product_id, demand
- ✅ Preprocesses: Adds weekday, month, year
- ✅ Sorts by date
- ✅ Shows date range

**What to Verify**:
- Dates parsed correctly
- Demand values are numeric
- Historical trend visible

---

### Test Case: Risk Assessment with Real Suppliers

**Steps**:
1. After uploading suppliers
2. Go to "Risk Assessment" tab
3. Search: "export controls [supplier location]"
4. Review supplier risk overview

**Expected Results**:
- ✅ Real suppliers from dataset appear
- ✅ Risk scores based on location
- ✅ High-risk suppliers highlighted (if from China/Russia)
- ✅ Tavily search returns relevant results

**What to Verify**:
- Suppliers from dataset are listed
- Risk scores are accurate
- Search works with real locations

---

### Test Case: Demand Forecasting with Real Data

**Steps**:
1. After uploading demand data
2. Go to "Demand Forecasting" tab
3. Select a product (SKU from dataset)
4. Generate 30-day forecast

**Expected Results**:
- ✅ Forecast based on real sales history
- ✅ Trend reflects actual patterns
- ✅ Confidence intervals reasonable
- ✅ Chart shows historical + forecast

**What to Verify**:
- Forecast uses real data
- Trend makes sense
- Values are realistic

---

### Test Case: Supplier Analysis with Real Suppliers

**Steps**:
1. After uploading suppliers
2. Go to "Supplier Analysis" tab
3. Select a supplier from dataset
4. Evaluate supplier

**Expected Results**:
- ✅ Shows supplier from dataset
- ✅ Location-based risk assessment
- ✅ Reliability score calculated
- ✅ Real-time risk if available

**What to Verify**:
- Supplier names match dataset
- Locations are correct
- Evaluation is accurate

---

### Test Case: Inventory Optimization with Real Products

**Steps**:
1. After uploading inventory
2. Go to "Inventory Optimization (RL)" tab
3. Select a product (SKU from dataset)
4. Get RL recommendation

**Expected Results**:
- ✅ Uses real stock levels
- ✅ Recommendation based on actual data
- ✅ Rationale references real values

**What to Verify**:
- Stock levels match dataset
- Recommendations are reasonable
- Model considers real constraints

---

## 🔄 Complete End-to-End Test Flow

### Scenario: Full Workflow with Real Dataset

1. **Upload Phase**
   - Upload suppliers → Verify count
   - Upload inventory → Verify products
   - Upload demand → Verify history

2. **Analysis Phase**
   - Dashboard → Check metrics match data
   - Risk Assessment → Search real locations
   - Demand Forecasting → Forecast real products
   - Supplier Analysis → Evaluate real suppliers

3. **Optimization Phase**
   - Inventory RL → Optimize real products
   - Logistics → Use real routes/carriers
   - Human Feedback → Provide feedback on real recommendations

4. **Integration Phase**
   - Comprehensive Analysis → End-to-end with real data
   - Demo Scenarios → Use real data context

---

## 📊 Dataset Mapping

### Original Dataset → Our System

| Original Column | Our System | Transformation |
|----------------|------------|----------------|
| Supplier name | supplier_name | Direct |
| Location | country | Direct |
| SKU | product_id | Direct |
| Stock levels | current_stock | Direct |
| Lead times | lead_time_days | Direct |
| Number of products sold | demand | Aggregate to daily |
| Price | unit_cost | Direct |

---

## ✅ Expected Test Results with Real Dataset

### Upload Results
- **Suppliers**: ~5-10 unique suppliers (based on dataset)
- **Products**: 100 products (all SKUs)
- **Demand**: 90 days of history (generated from sales)

### Analysis Results
- **Risk Assessment**: Suppliers from Mumbai, Kolkata, etc.
- **Demand Forecast**: Based on actual sales patterns
- **Supplier Evaluation**: Real supplier names and locations
- **Inventory Optimization**: Real stock levels and costs

### API Integration
- **Tavily**: Search for risks in supplier locations
- **NewsAPI**: Get supply chain news (if key valid)

---

## 🎯 Success Criteria

**With Real Dataset**:
- ✅ All data uploads successfully
- ✅ All tabs work with real data
- ✅ Charts show real patterns
- ✅ Recommendations use real values
- ✅ APIs search real locations
- ✅ End-to-end workflow completes

---

## 📝 Quick Test Commands

```bash
# Check dataset
python -c "import pandas as pd; df = pd.read_csv('~/Downloads/supply_chain_data.csv'); print(f'Rows: {len(df)}, Columns: {list(df.columns)[:5]}')"

# Run automated tests
python test_end_to_end.py

# Launch Streamlit
streamlit run streamlit_app.py
```

---

**Ready to Test with Real Data!** 🎉



