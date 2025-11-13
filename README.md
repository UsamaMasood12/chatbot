# Portfolio AI Chatbot - Phase 1 MVP

An intelligent AI-powered chatbot assistant for your portfolio website that answers questions about your professional background, skills, and projects using Retrieval-Augmented Generation (RAG).

## 🎯 Features (Phase 1)

### Core Conversational Features
- ✅ Multi-turn conversations with context retention
- ✅ Intent recognition and natural language understanding
- ✅ Graceful fallback handling for unknown queries
- ✅ Suggested questions to guide users

### Knowledge Coverage
- ✅ Complete CV/Resume information retrieval
- ✅ Project details and technical explanations
- ✅ Technical skills and expertise showcase
- ✅ Contact information provision
- ✅ Self-awareness about the chatbot itself

### RAG & Retrieval
- ✅ Semantic search using embeddings
- ✅ ChromaDB/FAISS vector store
- ✅ Source citations for transparency
- ✅ Context-aware retrieval

### UI/UX
- ✅ Minimalist collapsible chat widget
- ✅ Typing indicators
- ✅ Message timestamps
- ✅ Markdown rendering with syntax highlighting
- ✅ Mobile responsive design
- ✅ Smooth animations

### Security
- ✅ API key protection
- ✅ Input sanitization
- ✅ HTTPS ready
- ✅ CORS configuration

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓
FastAPI Backend
    ↓
LangChain RAG Pipeline
    ↓
Vector Store (ChromaDB/FAISS) + OpenAI GPT-4
```

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd portfolio-chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**Configure `.env` file:**
```
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_STORE_TYPE=chromadb
LLM_MODEL=gpt-4
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000/api/v1)
```

## 🎮 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m app.main
```

Backend will run on: `http://localhost:8000`
API Docs available at: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

## 📝 Customizing the Knowledge Base

### Update CV Information

Edit `/backend/data/cv.txt` with your own information:

```txt
YOUR NAME
YOUR TITLE

Contact Information:
- Location: Your Location
- Email: your.email@example.com
...
```

### Add Additional Context

Edit `/backend/data/context.txt` to add more information about yourself, your goals, and the chatbot.

### Recreate Vector Store

After updating knowledge base files:

```bash
cd backend
# Delete existing vector store
rm -rf vector_store/

# Restart the backend (it will recreate the vector store)
python -m app.main
```

## 🔧 Configuration

### Backend Configuration (`backend/app/config.py`)

Key settings you can modify:

```python
CHUNK_SIZE = 500           # Text chunk size for documents
CHUNK_OVERLAP = 50         # Overlap between chunks
TOP_K_RESULTS = 3          # Number of documents to retrieve
TEMPERATURE = 0.7          # LLM creativity (0-1)
MAX_TOKENS = 500           # Maximum response length
LLM_MODEL = "gpt-4"        # or "gpt-3.5-turbo"
```

### Frontend Configuration

Modify colors and styling in `/frontend/tailwind.config.js`:

```javascript
colors: {
  primary: {
    600: '#0284c7',  // Change primary color
  }
}
```

## 📡 API Endpoints

### POST `/api/v1/chat`
Send a message to the chatbot

**Request:**
```json
{
  "message": "What are Usama's main skills?",
  "conversation_history": [],
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "response": "Usama has expertise in...",
  "sources": [...],
  "conversation_id": "abc123",
  "model_used": "gpt-4",
  "processing_time": 1.23
}
```

### GET `/api/v1/health`
Check backend health status

### GET `/api/v1/suggestions`
Get suggested questions

### GET `/api/v1/info`
Get chatbot information

## 🎨 Embedding in Your Portfolio

### Option 1: Standalone Widget

The chatbot is already designed as a standalone widget. Just ensure your portfolio includes:

```jsx
import ChatBot from './components/ChatBot';

function YourPortfolio() {
  return (
    <div>
      {/* Your portfolio content */}
      <ChatBot />
    </div>
  );
}
```

### Option 2: Integration with Existing Site

Copy these files to your existing React project:
- `/frontend/src/components/ChatBot.jsx`
- `/frontend/src/services/api.js`
- `/frontend/src/styles/index.css` (merge with existing styles)

Then import and use the ChatBot component.

### Option 3: As a Separate Build

Build the frontend:
```bash
cd frontend
npm run build
```

Host the `dist/` folder separately and embed using an iframe in your main portfolio.

## 🐛 Troubleshooting

### Vector Store Not Creating
- Ensure `data/cv.txt` exists and has content
- Check file permissions
- Delete `vector_store/` folder and restart

### CORS Errors
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Ensure both frontend and backend are running

### OpenAI API Errors
- Verify your API key in `.env`
- Check OpenAI account has credits
- Try using `gpt-3.5-turbo` if rate limited

### Port Already in Use
```bash
# Backend
lsof -ti:8000 | xargs kill -9

# Frontend
lsof -ti:3000 | xargs kill -9
```

## 📊 Project Structure

```
portfolio-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── rag/
│   │   │   ├── vector_store.py  # Vector store management
│   │   │   └── chain.py         # RAG chain
│   │   └── knowledge/
│   │       └── loader.py        # Document loader
│   ├── data/
│   │   ├── cv.txt              # Your CV
│   │   └── context.txt         # Additional context
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatBot.jsx     # Main chatbot component
│   │   ├── services/
│   │   │   └── api.js          # API service
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env
│
└── README.md
```

## 🚀 Next Steps (Phase 2 & Beyond)

- [ ] Enhanced knowledge with project READMEs
- [ ] Hybrid search (semantic + keyword)
- [ ] Multi-LLM support
- [ ] Response streaming
- [ ] Chat history persistence
- [ ] Analytics dashboard
- [ ] Dark mode
- [ ] Voice input/output

## 📄 License

MIT License - feel free to use this for your own portfolio!

## 👤 Author

**Usama Masood**
- Portfolio: https://usamamasood12.github.io/Portfolio
- GitHub: [@UsamaMasood12](https://github.com/UsamaMasood12)
- LinkedIn: [Usama Masood](https://linkedin.com/in/masood-usama)

## 🙏 Acknowledgments

- Built with LangChain, OpenAI, FastAPI, and React
- RAG architecture inspired by enterprise AI applications
- UI design influenced by modern chat interfaces

---

**Made with ❤️ by Usama Masood**
