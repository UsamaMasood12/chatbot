# FREE Model Setup Guide

## 🎉 NO MORE API COSTS!

Your chatbot now supports **100% FREE models** - no OpenAI API costs!

---

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /home/user/chatbot/backend
pip install transformers==4.36.0 torch==2.1.2 accelerate==0.25.0 sentencepiece==0.1.99
```

### 2. Configuration Already Done!

Your `.env` or config already has:
```bash
USE_FREE_MODEL=True
FREE_MODEL_TYPE=huggingface
```

### 3. Start Backend

```bash
python -m app.main
```

**First start will download model (~ 1.5GB)** - takes 5-10 minutes one time only.

---

## Free Model Options

### Option 1: HuggingFace (RECOMMENDED - Completely Free)

**Pros:**
- ✅ 100% free, no API key needed
- ✅ Works offline once downloaded
- ✅ No rate limits
- ✅ Privacy (runs locally)

**Cons:**
- ⚠️ Slower (3-10 seconds per response)
- ⚠️ Requires 2-4GB RAM
- ⚠️ First download takes 5-10 min

**Models Available:**
- `google/flan-t5-large` (default, 780MB, good quality)
- `google/flan-t5-xl` (3GB, better quality, slower)
- `google/flan-t5-small` (300MB, faster, lower quality)

**Change model in `config.py`:**
```python
FREE_MODEL_NAME: str = "google/flan-t5-xl"  # For better quality
```

---

### Option 2: Groq API (FREE tier, FASTER)

**Pros:**
- ✅ 100% free tier available
- ✅ VERY FAST (1-2 seconds)
- ✅ High quality (Llama 3)
- ✅ No download needed

**Cons:**
- ⚠️ Requires free API key (easy to get)
- ⚠️ Rate limited (100 requests/day free)

**Setup:**

1. Get free API key: https://console.groq.com
2. Update config:
```python
USE_FREE_MODEL: bool = True
FREE_MODEL_TYPE: str = "groq"  # Changed from "huggingface"
GROQ_API_KEY: str = "gsk_your_free_key_here"
```

3. Restart backend

---

## Performance Comparison

| Model | Speed | Quality | Cost | Download |
|-------|-------|---------|------|----------|
| **GPT-4** | ⚡⚡⚡ Fast | 🌟🌟🌟🌟🌟 Best | 💰💰💰 $$$ | None |
| **GPT-3.5** | ⚡⚡⚡ Fast | 🌟🌟🌟🌟 Great | 💰💰 $$ | None |
| **Groq (Free)** | ⚡⚡⚡ Fast | 🌟🌟🌟🌟 Great | ✅ FREE | None |
| **FLAN-T5 Large** | ⚡ Slow | 🌟🌟🌟 Good | ✅ FREE | 780MB |
| **FLAN-T5 XL** | ⚡ Very Slow | 🌟🌟🌟🌟 Great | ✅ FREE | 3GB |

---

## Troubleshooting

### Model Download Fails

```bash
# Use smaller model
# In config.py:
FREE_MODEL_NAME: str = "google/flan-t5-small"
```

### Out of Memory

```bash
# Use smaller model
FREE_MODEL_NAME: str = "google/flan-t5-small"

# Or use Groq (cloud-based, no local memory needed)
FREE_MODEL_TYPE: str = "groq"
```

### Too Slow

```bash
# Option 1: Use Groq (much faster)
FREE_MODEL_TYPE: str = "groq"

# Option 2: Use smaller model (faster but lower quality)
FREE_MODEL_NAME: str = "google/flan-t5-small"
```

---

## Recommended Setup

**For Best Experience (Free + Fast):**
```python
USE_FREE_MODEL: bool = True
FREE_MODEL_TYPE: str = "groq"
GROQ_API_KEY: str = "your_free_key_from_groq.com"
```

**For Complete Privacy (No API, Offline):**
```python
USE_FREE_MODEL: bool = True
FREE_MODEL_TYPE: str = "huggingface"
FREE_MODEL_NAME: str = "google/flan-t5-large"
```

---

## Switch Back to OpenAI (If You Have Quota)

```python
USE_FREE_MODEL: bool = False
LLM_MODEL: str = "gpt-3.5-turbo"  # or "gpt-4"
OPENAI_API_KEY: str = "sk-your-key-here"
```

---

## Files Modified

- ✅ `backend/app/config.py` - Added free model settings
- ✅ `backend/app/rag/chain.py` - Added free model support
- ✅ `backend/app/rag/free_llm.py` - New file with free models
- ✅ `backend/requirements.txt` - Added transformers, torch
- ✅ `backend/app/main.py` - Pass free model params

---

## Next Steps

1. **Install dependencies** (see Quick Start above)
2. **Choose your option:**
   - Groq (fast + free API)
   - HuggingFace (completely offline)
3. **Start backend** and test!

No more API costs! 🎉

---

**Created:** 2025-11-13
**Status:** Ready to use
