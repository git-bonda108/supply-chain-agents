# Test Execution Guide

## 🚀 Quick Start

### 1. Prepare Test Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Ensure all dependencies installed
pip install -r requirements.txt

# Verify API keys
python -c "from utils.helpers import validate_api_keys; print(validate_api_keys())"
```

### 2. Find Test Datasets

```bash
# Find supply chain datasets in Downloads
find ~/Downloads -name "*.csv" -o -name "*.xlsx" | grep -iE "(supply|chain|inventory|supplier|demand)" | head -10

# Or run the test script to find them
python test_end_to_end.py
```

### 3. Run Automated Tests

```bash
# Run comprehensive end-to-end tests
python test_end_to_end.py

# Run integration tests
python test_all_integrations.py
```

### 4. Manual Testing with Streamlit

```bash
# Launch Streamlit
streamlit run streamlit_app.py

# Then manually test each tab following the test cases
```

---

## 📋 Test Execution Order

### Phase 1: Setup & Data Preparation
1. ✅ Verify environment
2. ✅ Find/upload test datasets
3. ✅ Verify API keys

### Phase 2: Core Functionality
1. Dashboard Tab
2. Data Upload & Analysis Tab
3. Risk Assessment Tab
4. Demand Forecasting Tab

### Phase 3: Advanced Features
5. Supplier Analysis Tab
6. Inventory Optimization (RL) Tab
7. Logistics Planning Tab
8. Human-in-the-Loop Learning Tab

### Phase 4: Integration
9. Comprehensive Analysis Tab
10. Demo Scenarios Tab
11. Cross-tab integration tests

---

## 📊 Expected Test Results Summary

| Tab | Key Functionality | Expected Result |
|-----|------------------|-----------------|
| **Dashboard** | Display metrics | Shows counts, charts render |
| **Data Upload** | Upload CSV/Excel | Validates, preprocesses, saves |
| **Risk Assessment** | Search risks | Returns results from Tavily API |
| **Demand Forecasting** | Generate forecast | Shows 7-day forecast with confidence |
| **Supplier Analysis** | Evaluate supplier | Shows reliability score, rating |
| **Inventory RL** | Get recommendation | Returns order quantity (0-2000) |
| **Logistics** | Optimize route | Shows route, time, cost |
| **Human Feedback** | Submit feedback | Saves feedback, updates model |
| **Comprehensive** | End-to-end analysis | Multi-agent report generated |
| **Demo Scenarios** | Run scenario | Executes pre-built scenario |

---

## 🎯 Success Criteria

### Overall System
- ✅ All tabs load without errors
- ✅ All API integrations work
- ✅ Data flows correctly between tabs
- ✅ No crashes or exceptions

### Data Processing
- ✅ Upload validation works
- ✅ Preprocessing completes
- ✅ Data saves correctly
- ✅ Charts render

### AI/ML Features
- ✅ Agents respond to queries
- ✅ RL model trains successfully
- ✅ Forecasts are generated
- ✅ Recommendations are reasonable

### User Experience
- ✅ Interface is responsive
- ✅ Error messages are clear
- ✅ Loading indicators show
- ✅ Results are displayed clearly

---

## 🐛 Troubleshooting

### Issue: No test data
**Solution**: Use mock data generator or create sample CSV files

### Issue: API errors
**Solution**: Check `.env` file, verify API keys are valid

### Issue: Import errors
**Solution**: Run `pip install -r requirements.txt`

### Issue: Slow performance
**Solution**: Check internet connection, reduce test data size

---

**Ready to Test!** 🧪



