# Launch Instructions

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
cd supply-chain-agents
source .venv/bin/activate
```

### 2. Launch Streamlit Application
```bash
streamlit run streamlit_app.py
```

### 3. Access Application
Open your browser to: **http://localhost:8501**

---

## 📋 Application Sections

Once launched, you'll see 10 sections in the sidebar:

1. **Dashboard** - Overview and key metrics
2. **Data Upload & Analysis** ⭐ - Upload your datasets
3. **Risk Assessment** - Geopolitical risk monitoring
4. **Demand Forecasting** - Demand prediction
5. **Supplier Analysis** - Supplier evaluation
6. **Inventory Optimization (RL)** ⭐ - RL-based optimization
7. **Logistics Planning** - Route optimization
8. **Human-in-the-Loop Learning** ⭐ - Provide feedback
9. **Comprehensive Analysis** - End-to-end analysis
10. **Demo Scenarios** - Pre-built scenarios

---

## 🎯 Recommended First Steps

### Step 1: Upload Your Data
1. Go to **"Data Upload & Analysis"**
2. Select data type (suppliers, inventory, or demand)
3. Upload CSV or Excel file
4. Click "Process Data"
5. Review data preview

### Step 2: Train RL Model
1. Go to **"Inventory Optimization (RL)"**
2. Select a product
3. Click "Train RL Model"
4. Set training episodes (1000 recommended)
5. Click "Start Training"
6. Wait for training to complete

### Step 3: Get Recommendations
1. In **"Inventory Optimization (RL)"**
2. Click "Get RL Recommendation"
3. Review the recommendation

### Step 4: Provide Feedback
1. Go to **"Human-in-the-Loop Learning"**
2. Get a system recommendation
3. Review and provide feedback (Approve/Reject/Modify)
4. Submit feedback
5. Model updates automatically

---

## 🔧 Troubleshooting

### Issue: Streamlit not launching
```bash
# Check if port 8501 is in use
lsof -ti:8501 | xargs kill -9

# Try different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Import errors
```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Issue: API key errors
- Check `.env` file exists
- Verify API keys are set correctly
- Restart Streamlit after updating `.env`

---

## ✅ System Ready!

The application is fully functional with:
- ✅ Data upload capability
- ✅ RL model training
- ✅ Human feedback system
- ✅ All 10 sections working
- ✅ Real data integration

**Launch and start using!** 🚀



