# Quick Test Reference Guide

## 🚀 Run Tests

```bash
# Activate environment
source .venv/bin/activate

# Run automated tests
python test_end_to_end.py

# Run integration tests
python test_all_integrations.py

# Launch Streamlit for manual testing
streamlit run streamlit_app.py
```

---

## 📋 Test Datasets Available

**From Downloads Folder**:
- ✅ `supply_chain_data.csv` (20.6 KB)
- ✅ `Batch4_Supply_Chain_MockData.xlsx` (17.9 KB)

**Location**: `~/Downloads/`

---

## ✅ Expected Results by Tab

### Dashboard
- Metrics: Counts display
- Charts: Render correctly
- Data: Updates when refreshed

### Data Upload
- Upload: Success message
- Validation: Shows errors if invalid
- Preview: First 10 rows displayed

### Risk Assessment
- Search: 2-10 results from Tavily
- Risk Score: 0-1 value
- Supplier Risk: Chart and table

### Demand Forecasting
- Forecast: 7-day prediction
- Trend: INCREASING/DECREASING/STABLE
- Chart: Line with confidence bands

### Supplier Analysis
- Evaluation: Reliability score (0-1)
- Rating: EXCELLENT/GOOD/FAIR/POOR
- Alternatives: List of options

### Inventory RL
- Recommendation: Order quantity (0-2000)
- Training: Progress chart
- Performance: Q-table size, rewards

### Human Feedback
- Approve: +50 reward
- Reject: -30 reward
- Modify: Variable reward
- History: Table of all feedback

### Comprehensive Analysis
- Report: Multi-agent output
- Format: Well-structured
- Agents: Multiple agents contribute

### Demo Scenarios
- Execution: Scenario runs
- Results: Match description
- Agents: Correct agents used

---

## 🎯 Success Criteria

**All Tabs**:
- ✅ Load without errors
- ✅ Display data correctly
- ✅ Handle user input
- ✅ Show results

**APIs**:
- ✅ Tavily: Returns results
- ✅ NewsAPI: Connects (may return 0 articles)
- ✅ OpenAI: Agents respond

**Data**:
- ✅ Uploads process
- ✅ Validation works
- ✅ Preprocessing completes
- ✅ Saves correctly

---

**Quick Reference Ready!** 📋



