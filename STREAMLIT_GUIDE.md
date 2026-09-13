# Streamlit Frontend Guide

## 🚀 Quick Start

### Run the Application

```bash
# Option 1: Using the script
./run_streamlit.sh

# Option 2: Direct command
source .venv/bin/activate
streamlit run streamlit_app.py
```

The application will open at: `http://localhost:8501`

## 📋 Application Sections

### 1. Dashboard
- **Overview**: Key metrics and KPIs
- **Supplier Risk Distribution**: Visual risk analysis
- **Inventory Status**: Current stock levels
- **Demand Trends**: Historical demand visualization

### 2. Risk Assessment
- **Geopolitical Risk Analysis**: Country and product risk assessment
- **Supplier Risk Overview**: Risk analysis by supplier
- **Real-time Risk Monitoring**: Using Tavily API

### 3. Demand Forecasting
- **Product Demand Forecast**: Generate forecasts for any product
- **Shortage Detection**: Identify potential stockouts
- **Historical Demand Visualization**: Trend analysis

### 4. Supplier Analysis
- **Supplier Evaluation**: Detailed supplier assessment
- **Alternative Suppliers**: Find replacement suppliers
- **Supplier Comparison**: Compare multiple suppliers

### 5. Inventory Optimization
- **Inventory Optimization**: Calculate optimal stock levels
- **Reorder Point Calculation**: Determine when to reorder
- **Current Inventory Status**: Visual inventory dashboard

### 6. Logistics Planning
- **Route Optimization**: Find optimal shipping routes
- **Transportation Mode Comparison**: Compare air, sea, rail
- **Risk-Adjusted Routing**: Consider geopolitical risks

### 7. Comprehensive Analysis
- **End-to-End Analysis**: Complete supply chain analysis
- **Multi-Agent Coordination**: All agents working together
- **Executive Summary**: Comprehensive reporting

### 8. Demo Scenarios
- **Pre-built Scenarios**: 5 ready-to-use scenarios
- **One-Click Execution**: Run complete workflows
- **Scenario Results**: Detailed analysis output

## 🎯 Features

### Interactive Elements
- ✅ **Buttons**: Primary action buttons for all operations
- ✅ **Selectboxes**: Dropdown menus for data selection
- ✅ **Sliders**: Adjustable parameters (forecast days, service levels)
- ✅ **Multiselect**: Multiple option selection
- ✅ **Checkboxes**: Toggle options

### Data Visualization
- ✅ **Plotly Charts**: Interactive charts and graphs
- ✅ **Metrics**: Key performance indicators
- ✅ **Data Tables**: Sortable and filterable tables
- ✅ **Real-time Updates**: Live data from APIs

### User Experience
- ✅ **Sidebar Navigation**: Easy section switching
- ✅ **Status Indicators**: API key status, loading states
- ✅ **Error Handling**: Clear error messages
- ✅ **Success Messages**: Confirmation of actions

## 🧪 Testing

### Run Tests
```bash
python tests/test_streamlit.py
```

### Test Coverage
- ✅ Data loading functions
- ✅ Data integrity checks
- ✅ Scenario management
- ✅ Agent integration
- ✅ Real data usage verification

## 📊 Real Data Integration

The application uses **real data** from:
- **Supplier Database**: Actual supplier records
- **Inventory System**: Current stock levels
- **Demand History**: Historical demand data
- **Real-time APIs**: Tavily and NewsAPI for live data

### Data Sources
1. **CSV Files**: `data/processed/` directory
2. **Data Loader**: Automatic data loading and caching
3. **API Integration**: Real-time risk and news data
4. **Fallback**: Mock data generator if needed

## 🎨 UI Components

### Color Scheme
- **Primary**: Blue (#1f77b4)
- **Success**: Green (#d4edda)
- **Warning**: Yellow (#fff3cd)
- **Error**: Red (#f8d7da)

### Layout
- **Wide Layout**: Maximum screen utilization
- **Columns**: Responsive column layouts
- **Cards**: Metric cards and info boxes
- **Dividers**: Section separation

## 🔧 Configuration

### Environment Variables
Ensure `.env` file contains:
- `OPENAI_API_KEY`: Required for agents
- `TAVILY_API_KEY`: For real-time risk data
- `NEWSAPI_KEY`: For supply chain news

### API Status
Check sidebar for API key status indicators.

## 📝 Usage Examples

### Example 1: Risk Assessment
1. Navigate to "Risk Assessment"
2. Select country (e.g., "China")
3. Enter product (e.g., "Memory Chips")
4. Click "Assess Risk"
5. View results with risk score and recommendations

### Example 2: Demand Forecast
1. Navigate to "Demand Forecasting"
2. Select product from dropdown
3. Adjust forecast period slider
4. Click "Generate Forecast"
5. View forecast with confidence intervals

### Example 3: Comprehensive Analysis
1. Navigate to "Comprehensive Analysis"
2. Select analysis components
3. Click "Run Comprehensive Analysis"
4. Wait for multi-agent orchestration
5. View executive summary

## 🐛 Troubleshooting

### Issue: API Key Errors
**Solution**: Check `.env` file and ensure all API keys are set

### Issue: Data Not Loading
**Solution**: Run `python tools/mock_data_generator.py` to generate data

### Issue: Agents Not Responding
**Solution**: Verify OpenAI API key is valid and has credits

### Issue: Slow Performance
**Solution**: Enable caching in settings, use cached data options

## ✅ Best Practices

1. **Use Cached Data**: Enable caching for faster responses
2. **Selective Analysis**: Choose specific components for faster results
3. **Monitor API Status**: Check sidebar for API key status
4. **Review Results**: Always review agent outputs for accuracy
5. **Export Data**: Use Streamlit's built-in export features

## 🎓 For the Demo

### Recommended Demo Flow
1. **Start with Dashboard**: Show overview
2. **Risk Assessment**: Demonstrate real-time risk monitoring
3. **Supplier Analysis**: Show supplier evaluation
4. **Comprehensive Analysis**: Full system demonstration
5. **Demo Scenarios**: Run pre-built scenarios

### Key Talking Points
- Real-time data integration (Tavily, NewsAPI)
- Multi-agent orchestration
- Comprehensive analysis capabilities
- User-friendly interface
- Production-ready system

---

**Built with Streamlit for Supply Chain AI Demo**



