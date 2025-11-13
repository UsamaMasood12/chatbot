# Setup Instructions After Merging PR

## 🎉 You merged the PR! Here's what to do next:

---

## Step 1: Get Free Groq API Key (2 minutes)

1. Go to: **https://console.groq.com**
2. Sign up (free, no credit card)
3. Click "API Keys" in sidebar
4. Click "Create API Key"
5. Copy your key (starts with `gsk_`)

---

## Step 2: Add Key to .env File

```bash
cd backend
nano .env
```

Find this line:
```
GROQ_API_KEY=
```

Change it to:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## Step 3: Install Dependencies (one time)

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- Transformers, torch (for local models)
- All other dependencies

**Takes:** 5-10 minutes

---

## Step 4: Delete Old Vector Store (Important!)

```bash
cd backend
rm -rf vector_store
```

**Why?** Old vector store has wrong age (25 instead of 26)

---

## Step 5: Start Backend

```bash
cd backend
python -m app.main
```

**You should see:**
```
✅ FREE model initialized: groq
Portfolio Chatbot API started successfully!
```

---

## Step 6: Test It!

Open your chatbot and ask:
- "How old is Usama?" → Should say **26 years old**
- "What is Usama's email?" → Should be consistent every time

Ask the same question 3 times - should get same core facts!

---

## Troubleshooting

### If you see "GROQ_API_KEY not set"
- Make sure you added your key to `.env` file
- Make sure no spaces: `GROQ_API_KEY=gsk_...` (not `GROQ_API_KEY= gsk_...`)
- Restart backend after editing `.env`

### If Groq doesn't work
The system will automatically fall back to HuggingFace (slower, but works offline)

### If backend crashes
Check logs:
```bash
tail -50 /tmp/backend_groq.log
```

---

## What Changed in This PR

### 1. ✅ Consistency Fixes
- Age corrected: 25 → 26 years old
- Temperature lowered: 0.7 → 0.2 (more consistent)
- Prompt improved: enforces identical answers

### 2. ✅ FREE Model Support
- Groq API integration (fast, free)
- HuggingFace fallback (offline, free)
- No more OpenAI costs!

### 3. ✅ Test Improvements
- Better test accuracy
- 30+ test issues fixed
- New documentation

### 4. ✅ Cleanup
- Removed unnecessary files
- Better .gitignore
- Comprehensive documentation

---

## Cost Comparison

| Model | Before | After |
|-------|--------|-------|
| OpenAI GPT-4 | $1-5/day | **$0.00** |
| OpenAI GPT-3.5 | $0.10-0.50/day | **$0.00** |
| Groq (Free) | N/A | **$0.00** |

**Savings:** ~$30-150/month 💰

---

## Quick Reference

**Configuration:** `backend/app/config.py`
**Environment:** `backend/.env`
**Free LLM code:** `backend/app/rag/free_llm.py`

**Get Groq Key:** https://console.groq.com

---

## Need Help?

**Issue:** Groq key not working
**Solution:** Double-check you copied the full key (starts with `gsk_`)

**Issue:** Too slow
**Solution:** Make sure you're using Groq, not HuggingFace

**Issue:** Wrong answers
**Solution:** Delete vector_store folder and restart

---

**That's it! Your chatbot is now FREE and consistent! 🎉**
