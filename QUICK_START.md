# Quick Start Guide
## Get Your Supply Chain AI Demo Running in 30 Minutes

---

## ⚡ Fast Track Setup

### Step 1: Install Dependencies (5 min)

```bash
# Navigate to project directory
cd supply-chain-agents

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Environment (2 min)

```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Or manually create .env file with:
# OPENAI_API_KEY=sk-...
```

### Step 3: Download Sample Data (10 min)

**Option A: Use Kaggle Datasets**
```bash
# Install Kaggle CLI
pip install kaggle

# Download datasets (replace with actual dataset names)
kaggle datasets download -d <dataset-name> -p data/raw/
```

**Option B: Use Mock Data** (for quick testing)
```python
# Create data directory
mkdir -p data/raw data/processed

# Generate mock data (implement in utils/mock_data_generator.py)
python -c "from utils.mock_data_generator import generate_data; generate_data()"
```

### Step 4: Run Basic Demo (5 min)

```bash
# Run main demo
python main.py

# Or run with specific query
python main.py "Assess risks for memory chip supply chain"
```

---

## 🎯 Next Steps

### Immediate (Today)
1. ✅ Install dependencies
2. ✅ Set up environment
3. ✅ Run basic demo
4. ✅ Review documentation

### This Week
1. **Day 1-2**: Implement core agents
   - Risk Intelligence Agent
   - Demand Forecasting Agent
   - Supplier Assessment Agent

2. **Day 3-4**: Set up data pipeline
   - Load Kaggle datasets
   - Create data access tools
   - Preprocess data

3. **Day 5**: Implement orchestration
   - Create orchestrator agent
   - Set up handoffs
   - Test workflows

### Next Week
1. Complete remaining agents
2. Integrate all components
3. Create demo scenarios
4. Build UI (optional)

---

## 📋 Checklist

### Setup
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] OpenAI API key configured
- [ ] Project structure created

### Development
- [ ] Core agents implemented
- [ ] Tools created
- [ ] Data pipeline set up
- [ ] Orchestration working
- [ ] Basic tests passing

### Demo
- [ ] Demo scenarios ready
- [ ] Data loaded
- [ ] Agents tested
- [ ] Documentation complete

---

## 🔧 Troubleshooting

### Issue: Import errors
```bash
# Make sure you're in the project directory
cd supply-chain-agents

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: OpenAI API errors
```bash
# Check API key
cat .env  # Should show OPENAI_API_KEY=sk-...

# Test API key
python -c "import openai; print(openai.api_key)"
```

### Issue: Missing data
```bash
# Create data directories
mkdir -p data/raw data/processed

# Download sample data or generate mock data
```

---

## 📚 Documentation Quick Links

- **Full Plan**: [SUPPLY_CHAIN_DEMO_PLAN.md](./SUPPLY_CHAIN_DEMO_PLAN.md)
- **Implementation**: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- **Orchestration**: [MULTI_AGENT_ORCHESTRATION.md](./MULTI_AGENT_ORCHESTRATION.md)
- **Datasets**: [DATASET_RECOMMENDATIONS.md](./DATASET_RECOMMENDATIONS.md)
- **Summary**: [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)

---

## 🎓 Learning Path

### Beginner
1. Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)
2. Review [MULTI_AGENT_ORCHESTRATION.md](./MULTI_AGENT_ORCHESTRATION.md)
3. Run basic demo
4. Explore agent code

### Intermediate
1. Study [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
2. Implement one agent
3. Create custom tools
4. Test handoffs

### Advanced
1. Build complete workflow
2. Optimize performance
3. Add custom features
4. Deploy to production

---

## 💡 Example Queries to Try

### Risk Assessment
```
"Assess the risk for our memory chip supply chain from China"
```

### Demand Forecasting
```
"Predict demand for component X over the next 6 months"
```

### Supplier Evaluation
```
"Evaluate our current suppliers and recommend alternatives"
```

### Inventory Optimization
```
"Optimize inventory levels for product Y considering current risks"
```

### Comprehensive Analysis
```
"We're seeing delays in memory chip deliveries. Assess the situation, predict demand, evaluate suppliers, and recommend actions"
```

---

## 🚀 Production Considerations

### When Moving to Production

1. **Session Management**
   - Switch from SQLite to Redis
   - Implement session cleanup
   - Add session security

2. **Error Handling**
   - Add retry logic
   - Implement fallbacks
   - Log errors properly

3. **Performance**
   - Add caching
   - Optimize agent calls
   - Use parallel execution

4. **Security**
   - Secure API keys
   - Validate inputs
   - Add rate limiting

5. **Monitoring**
   - Add logging
   - Track metrics
   - Set up alerts

---

## 📞 Getting Help

### Resources
- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/)
- [GitHub Issues](https://github.com/openai/openai-agents-python/issues)
- [Community Discussions](https://github.com/openai/openai-agents-python/discussions)

### Common Questions

**Q: How do I add a new agent?**
A: Create agent file in `agents/`, add to orchestrator handoffs, update configs.

**Q: How do I add custom tools?**
A: Create tool function, wrap with `Tool()`, add to agent's tools list.

**Q: How do I test agents?**
A: Use `Runner.run()` with test queries, check `result.final_output`.

**Q: How do I improve agent responses?**
A: Refine instructions in `config/agent_configs.py`, add better tools, provide examples.

---

## ✅ Success Criteria

You're ready when:
- ✅ All agents can be instantiated
- ✅ Basic queries return results
- ✅ Handoffs work between agents
- ✅ Data pipeline loads data
- ✅ Demo scenarios run successfully

---

**Happy Building! 🚀**

*For detailed information, refer to the comprehensive documentation files.*



