# Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.10+
- Virtual environment
- All API keys configured
- Server with sufficient resources

### Step 1: Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd "Supply Chain"

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

Create `.env` file with all required API keys:

```bash
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
NEWSAPI_KEY=your_key
# ... other keys
```

### Step 3: Run Tests

```bash
python test_all_integrations.py
```

Ensure all tests pass before deployment.

### Step 4: Launch Application

#### Option A: Streamlit (Development)
```bash
streamlit run streamlit_app.py
```

#### Option B: Production with PM2
```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start streamlit_app.py --name supply-chain-agents --interpreter python3

# Save PM2 configuration
pm2 save
```

#### Option C: Docker (Recommended for Production)
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 5: Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 6: SSL Certificate

```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] `.env` file excluded from git
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Error logging configured
- [ ] Regular backups scheduled

---

## 📊 Monitoring

### Health Checks
- API endpoint availability
- Database connectivity
- API key validity
- Model performance

### Logging
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: Configured in Nginx

---

## 🔄 Updates

### Update Process
1. Pull latest code
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Run tests: `python test_all_integrations.py`
4. Restart application
5. Verify functionality

---

## 🐛 Troubleshooting

### Issue: Application won't start
- Check Python version: `python --version`
- Verify dependencies: `pip list`
- Check API keys: `python -c "from utils.helpers import validate_api_keys; print(validate_api_keys())"`

### Issue: API errors
- Verify API keys in `.env`
- Check API rate limits
- Review error logs

### Issue: Performance issues
- Check server resources
- Review cache configuration
- Optimize database queries

---

**Ready for Production!** 🚀



