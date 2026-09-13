# 🚀 Streamlit Deployment Guide

## 📋 Main File Path

**Primary Application File:**
```
streamlit_app.py
```

**Deployment Command:**
```bash
streamlit run streamlit_app.py
```

---

## 🔑 Required API Keys

### Core API Keys (Required)

| API Key | Environment Variable | Purpose | Status |
|---------|-------------------|---------|--------|
| **OpenAI** | `OPENAI_API_KEY` | Multi-agent orchestration | ✅ Configured |
| **Tavily** | `TAVILY_API_KEY` | Real-time geopolitical risk search | ✅ Configured |
| **NewsAPI** | `NEWSAPI_KEY` | Supply chain news aggregation | ✅ Configured |

### Optional API Keys (Backup Providers)

| API Key | Environment Variable | Purpose | Status |
|---------|-------------------|---------|--------|
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude AI (backup) | ✅ Configured |
| **DeepSeek** | `DEEPSEEK_API_KEY` | DeepSeek AI (backup) | ✅ Configured |
| **Groq** | `GROQ_API_KEY` | Groq AI (backup) | ✅ Configured |
| **Gemini** | `GEMINI_API_KEY` | Google Gemini (backup) | ✅ Configured |
| **Serper** | `SERPER_API_KEY` | Serper search (backup) | ✅ Configured |

---

## 📝 API Keys Configuration

### API Keys Template (add to `.env` file):

```bash
# Required Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
NEWSAPI_KEY=your_newsapi_key_here

# Optional Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

**Note:** Replace placeholder values with your actual API keys. Keys are stored in `.env` file (not committed to Git).

---

## 🚀 Quick Deployment Steps

### 1. Local Deployment

```bash
# Navigate to project directory
cd "Supply Chain"

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Streamlit app
streamlit run streamlit_app.py
```

**Access at:** `http://localhost:8501`

### 2. Streamlit Cloud Deployment

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `streamlit_app.py` as the main file
   - Add environment variables (API keys) in the settings
   - Deploy!

### 3. Environment Variables for Streamlit Cloud

Add these environment variables in Streamlit Cloud settings (replace with your actual keys):

```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
NEWSAPI_KEY=your_newsapi_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

**Important:** Never commit actual API keys to the repository. Always use environment variables.

---

## 📁 Project Structure

```
Supply Chain/
├── streamlit_app.py          ← Main Streamlit application file
├── .env                      ← API keys (not in git)
├── requirements.txt          ← Dependencies
├── supply_chain_agents/      ← AI agents
├── tools/                    ← Tools and utilities
├── ml_models/                ← ML models
└── utils/                   ← Helper functions
```

---

## ✅ Pre-Deployment Checklist

- [x] All API keys configured in `.env`
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Virtual environment activated
- [x] Streamlit app tested locally
- [x] All imports working
- [x] UI enhancements applied

---

## 🎨 UI Features

The updated UI includes:
- ✨ Beautiful gradient title with icons
- 🎯 Compelling taglines
- 🏷️ Feature pills with hover effects
- 🎨 Professional color scheme
- 📱 Responsive design

---

## 🔒 Security Notes

- `.env` file is excluded from Git (via `.gitignore`)
- API keys should never be committed to repository
- For Streamlit Cloud, add keys via environment variables in settings
- Rotate keys regularly for security

---

## 📞 Support

For deployment issues:
1. Check API keys are set correctly
2. Verify all dependencies are installed
3. Check Streamlit version: `streamlit --version`
4. Review error logs in terminal

---

**Ready to Deploy! 🚀**

