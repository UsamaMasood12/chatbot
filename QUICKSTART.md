# 🚀 Quick Start Guide - Portfolio Chatbot Phase 1

Get your AI chatbot running in 10 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if you have pip
pip --version

# Check if you have npm
npm --version
```

## Step-by-Step Setup

### 1️⃣ Get OpenAI API Key (2 minutes)

1. Go to https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### 2️⃣ Backend Setup (3 minutes)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file and add your OpenAI key
# Open .env in any text editor and replace:
# OPENAI_API_KEY=your_openai_api_key_here
# with your actual key
```

### 3️⃣ Customize Your Information (2 minutes)

```bash
# Edit your CV information
# Open backend/data/cv.txt in a text editor
# Replace with YOUR information

# Edit additional context
# Open backend/data/context.txt
# Add more details about yourself
```

### 4️⃣ Frontend Setup (2 minutes)

```bash
# Navigate to frontend (from backend folder)
cd ../frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# No need to edit .env unless you changed backend port
```

### 5️⃣ Start Everything (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main
```

You should see:
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in X ms

  ➜  Local:   http://localhost:3000/
```

### 6️⃣ Test It! 

1. Open browser to `http://localhost:3000`
2. Click the chat icon in bottom-right corner
3. Ask: "What are Usama's main skills?"
4. Watch the magic happen! ✨

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'X'"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Kill the process using port 8000
# On Mac/Linux:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "OpenAI API Error"
- Check your API key is correct in `.env`
- Ensure you have credits in your OpenAI account
- Try changing `LLM_MODEL=gpt-3.5-turbo` in `.env` (cheaper)

### Vector Store Not Creating
```bash
# Delete and recreate
cd backend
rm -rf vector_store/
python -m app.main
```

### CORS Error in Browser
Check `backend/.env` has:
```
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## What to Customize Next

### 1. Update Your Information
- Edit `backend/data/cv.txt` with YOUR CV
- Edit `backend/data/context.txt` with YOUR story
- Restart backend to reload

### 2. Change Colors
Edit `frontend/tailwind.config.js`:
```javascript
primary: {
  600: '#YOUR_COLOR',  // Main button color
}
```

### 3. Modify Chatbot Personality
Edit the prompt in `backend/app/rag/chain.py` in the `_create_prompt()` function

### 4. Add More Documents
Add `.txt` or `.md` files to `backend/data/`
Restart backend to index them

## Testing Your Chatbot

Good test questions:
1. "What is Usama's email?"
2. "Tell me about the RAG projects"
3. "What programming languages does Usama know?"
4. "Describe Usama's educational background"
5. "How does this chatbot work?"

## Deployment Checklist

Before deploying to production:

- [ ] Update all personal information in data files
- [ ] Set strong API keys
- [ ] Change DEBUG=False in backend/.env
- [ ] Update CORS_ORIGINS to your production domain
- [ ] Use environment-specific API URLs
- [ ] Consider using gpt-3.5-turbo for cost savings
- [ ] Set up monitoring/logging
- [ ] Add rate limiting for production

## Get Help

If stuck:
1. Check the full README.md
2. Look at error messages carefully
3. Ensure all prerequisites are installed
4. Verify file paths are correct
5. Check both backend and frontend are running

## Success! 🎉

Your chatbot should now be working! Continue to Phase 2 for advanced features:
- Multi-LLM support
- Response streaming  
- Analytics
- Enhanced UI/UX
- And much more!

---

**Time Spent:** ~10 minutes
**Skills Demonstrated:** RAG, LangChain, FastAPI, React, AI Engineering
**Result:** A working AI assistant for your portfolio! 🚀
