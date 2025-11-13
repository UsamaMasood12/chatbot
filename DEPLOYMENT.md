# 🚀 Deployment Guide - Portfolio Chatbot

Complete guide for deploying your chatbot to production.

---

## Deployment Options Overview

| Platform | Backend | Frontend | Cost | Difficulty | Best For |
|----------|---------|----------|------|------------|----------|
| **Render** | ✅ | ✅ | Free tier | Easy | Quick deployment |
| **Railway** | ✅ | ✅ | $5/month | Easy | Simple projects |
| **Vercel + Railway** | Railway | Vercel | ~$5/month | Medium | Fast frontends |
| **AWS** | Lambda/EC2 | S3+CloudFront | Pay-as-you-go | Hard | Enterprise |
| **DigitalOcean** | Droplet | Droplet | $6/month | Medium | Full control |
| **Heroku** | ✅ | ✅ | $7/month | Easy | Hobby projects |

---

## Option 1: Render.com (Recommended for Beginners)

### Advantages
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Built-in SSL
- ✅ Easy environment variables

### Backend Deployment

1. **Prepare Repository**
```bash
cd portfolio-chatbot
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Create render.yaml**
```yaml
services:
  - type: web
    name: portfolio-chatbot-api
    env: python
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && python -m app.main
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 8000
```

3. **Deploy to Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select "portfolio-chatbot"
   - Add environment variables
   - Click "Create Web Service"

4. **Configure Environment Variables**
   - OPENAI_API_KEY: your-key
   - VECTOR_STORE_PATH: /opt/render/project/src/vector_store
   - CORS_ORIGINS: ["https://your-frontend.vercel.app"]

### Frontend Deployment

1. **Update API URL**
Edit `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

2. **Deploy to Render**
   - New "Static Site"
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`

---

## Option 2: Vercel (Frontend) + Railway (Backend)

### Backend on Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
railway login
```

2. **Deploy Backend**
```bash
cd backend
railway init
railway up
```

3. **Add Environment Variables**
```bash
railway variables set OPENAI_API_KEY=your-key
railway variables set PORT=8000
```

4. **Get Backend URL**
```bash
railway domain
# Copy the URL (e.g., https://xyz.railway.app)
```

### Frontend on Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Update Environment**
Create `frontend/.env.production`:
```bash
VITE_API_URL=https://your-railway-url.railway.app/api/v1
```

3. **Deploy**
```bash
cd frontend
vercel --prod
```

4. **Set Environment Variables**
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add VITE_API_URL

---

## Option 3: AWS (Production-Grade)

### Backend on AWS Lambda + API Gateway

1. **Install AWS SAM CLI**
```bash
pip install aws-sam-cli
```

2. **Create SAM Template** (`backend/template.yaml`)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ChatbotFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.main.handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 1024
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAIKey
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Parameters:
  OpenAIKey:
    Type: String
    NoEcho: true
```

3. **Deploy**
```bash
cd backend
sam build
sam deploy --guided
```

### Frontend on S3 + CloudFront

1. **Build Frontend**
```bash
cd frontend
npm run build
```

2. **Create S3 Bucket**
```bash
aws s3 mb s3://your-portfolio-chatbot
aws s3 sync dist/ s3://your-portfolio-chatbot
```

3. **Configure CloudFront**
   - Create CloudFront distribution
   - Origin: S3 bucket
   - Enable HTTPS
   - Add custom domain (optional)

---

## Option 4: DigitalOcean Droplet

### Setup Droplet

1. **Create Droplet**
   - OS: Ubuntu 22.04
   - Plan: Basic $6/month
   - Add SSH key

2. **SSH into Droplet**
```bash
ssh root@your-droplet-ip
```

3. **Install Dependencies**
```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3.11 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Nginx
apt install nginx -y

# Install Certbot (for SSL)
apt install certbot python3-certbot-nginx -y
```

### Deploy Backend

```bash
# Clone repository
cd /opt
git clone <your-repo-url> portfolio-chatbot
cd portfolio-chatbot/backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# Add your environment variables

# Create systemd service
cat > /etc/systemd/system/chatbot.service << EOF
[Unit]
Description=Portfolio Chatbot Backend
After=network.target

[Service]
User=root
WorkingDirectory=/opt/portfolio-chatbot/backend
Environment="PATH=/opt/portfolio-chatbot/backend/venv/bin"
ExecStart=/opt/portfolio-chatbot/backend/venv/bin/python -m app.main

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl enable chatbot
systemctl start chatbot
```

### Deploy Frontend

```bash
# Build frontend
cd /opt/portfolio-chatbot/frontend
npm install
npm run build

# Copy to Nginx
cp -r dist/* /var/www/html/
```

### Configure Nginx

```bash
cat > /etc/nginx/sites-available/chatbot << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Setup SSL

```bash
certbot --nginx -d your-domain.com
```

---

## Option 5: Docker Deployment (Any Platform)

### Build Docker Images

**Backend Dockerfile** (already created):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

**Frontend Dockerfile**:
```dockerfile
# Build stage
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend/vector_store:/app/vector_store
      - ./backend/data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Deploy

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Post-Deployment Checklist

### Security
- [ ] HTTPS/SSL enabled
- [ ] API keys in environment variables (not code)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation working
- [ ] Error messages don't leak sensitive info

### Performance
- [ ] Vector store loaded successfully
- [ ] API response time < 3 seconds
- [ ] Frontend loads < 2 seconds
- [ ] Mobile responsive
- [ ] Caching configured

### Monitoring
- [ ] Error logging set up
- [ ] API monitoring (UptimeRobot, Pingdom)
- [ ] OpenAI usage tracking
- [ ] User analytics (optional)

### Documentation
- [ ] Update README with live URLs
- [ ] Document any custom setup steps
- [ ] Note any platform-specific configurations

---

## Cost Optimization

### Reduce OpenAI Costs

1. **Use GPT-3.5-turbo instead of GPT-4**
```bash
# In .env
LLM_MODEL=gpt-3.5-turbo  # ~10x cheaper
```

2. **Implement Response Caching**
```python
# Cache frequent questions
CACHE = {
    "what are usama's skills": "cached_response..."
}
```

3. **Reduce Token Usage**
```bash
MAX_TOKENS=300  # Instead of 500
CHUNK_SIZE=400  # Instead of 500
TOP_K_RESULTS=2  # Instead of 3
```

4. **Set Monthly Limits**
   - OpenAI Dashboard → Usage limits
   - Set hard limit (e.g., $10/month)

### Free Tier Options

- **Hosting:** Render.com (free)
- **Frontend:** Vercel/Netlify (free)
- **LLM:** Use Ollama locally (free, but slower)
- **Vector DB:** ChromaDB (free, self-hosted)

---

## Domain Setup

### Point Domain to Deployment

**For Vercel/Render:**
1. Add custom domain in dashboard
2. Update DNS records:
```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
```

**For DigitalOcean:**
```
Type: A
Name: @
Value: your-droplet-ip
```

---

## Monitoring & Maintenance

### Setup Monitoring

**Backend Health Check:**
```bash
# Add to crontab
*/5 * * * * curl https://your-api.com/api/v1/health
```

**UptimeRobot:**
- Create monitor for /health endpoint
- Email alerts on downtime

### Regular Maintenance

**Weekly:**
- Check OpenAI costs
- Review error logs
- Test chatbot functionality

**Monthly:**
- Update dependencies
- Review and update knowledge base
- Analyze usage patterns

---

## Troubleshooting Deployment Issues

### Backend Not Starting
```bash
# Check logs
docker logs <container-id>
# or
systemctl status chatbot
```

### Vector Store Issues
```bash
# Clear and rebuild
rm -rf vector_store/
# Restart application (will auto-rebuild)
```

### CORS Errors
```bash
# Update backend .env
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### SSL Certificate Issues
```bash
# Renew certificate
certbot renew
systemctl reload nginx
```

---

## Rollback Strategy

### If Deployment Fails

**Render/Vercel:**
- Revert to previous deployment in dashboard

**Docker:**
```bash
docker-compose down
git checkout <previous-commit>
docker-compose up -d
```

**DigitalOcean:**
```bash
systemctl stop chatbot
git reset --hard <previous-commit>
systemctl start chatbot
```

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **AWS SAM Docs:** https://docs.aws.amazon.com/serverless-application-model
- **DigitalOcean Tutorials:** https://www.digitalocean.com/community/tutorials

---

## Next Steps After Deployment

1. **Test thoroughly** - Try various questions
2. **Share the link** - Add to your resume/LinkedIn
3. **Gather feedback** - Ask friends to try it
4. **Monitor usage** - Track costs and performance
5. **Iterate** - Add Phase 2 features!

---

**🎉 Congratulations on deploying your AI chatbot!**

Your portfolio now has an interactive AI assistant that showcases your skills in:
- AI/ML Engineering
- Full-Stack Development
- RAG Architecture
- Cloud Deployment
- Production Systems

Keep building and improving! 🚀
