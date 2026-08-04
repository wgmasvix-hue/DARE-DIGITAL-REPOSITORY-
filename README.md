# rosersg: AI-Powered Assistant for DARE Digital Repository

An intelligent AI system that seamlessly integrates into DSpace 9 (repo.dare.co.zw), providing advanced semantic search, metadata optimization, content recommendations, and interactive conversational assistance powered by Ollama LLM.

## 🎯 What is rosersg?

rosersg is a complete AI stack for digital repositories:

- **💬 Interactive Chat**: Ask questions about research in your repository
- **🔍 Smart Search**: AI-enhanced search with semantic understanding
- **📝 Metadata Optimization**: Automatic improvement suggestions
- **⭐ Recommendations**: Discover related research items
- **📊 Collection Insights**: AI-generated analytics about your collections

All of this is seamlessly embedded into your DSpace interface - users never leave the repository domain!

## 📦 Project Structure

```
DARE-DIGITAL-REPOSITORY-/
├── rosersg.py                          # Flask REST API backend
├── rosersg-config.json                 # Configuration file
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Multi-service orchestration
├── .env.example                        # Environment template
├── setup.sh                            # Quick setup script
│
├── ui/                                 # React frontend
│   ├── src/
│   │   ├── App.jsx                    # Main app component
│   │   ├── App.css                    # Styling
│   │   └── index.jsx                  # Entry point
│   ├── package.json
│   └── public/index.html
│
├── Documentation/
│   ├── ROSERSG.md                     # Complete architecture & API docs
│   ├── QUICKSTART.md                  # Get running in 30 seconds
│   ├── EMBED_IN_DSPACE.md             # Angular components (full code)
│   ├── EMBEDDED_QUICK_START.md        # 30-min embedding guide
│   ├── DSPACE_INTEGRATION.md          # 10-step integration guide
│   ├── DEPLOY_DSPACE_LIVE.md          # Production deployment
│   ├── DSPACE9_INTEGRATION_CHECKLIST.md    # Step-by-step checklist (NEW!)
│   └── DSPACE_API_REFERENCE.md        # API endpoint reference (NEW!)
│
└── .github/                           # GitHub config
```

## 🚀 Quick Start (On Your Server)

### For Local Development/Testing

```bash
# 1. Clone and setup
git clone -b claude/rosersg-ollama-dspace-ai-b9tvxu \
  https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git
cd DARE-DIGITAL-REPOSITORY-

# 2. Configure
cp .env.example .env
# Edit .env with your settings

# 3. Start services
docker compose up -d

# 4. Wait 2-3 minutes for Ollama initialization
sleep 180

# 5. Verify
curl http://localhost:5000/health
curl http://localhost:3000
```

**Services Running:**
- API: http://localhost:5000
- Frontend: http://localhost:3000
- Ollama: http://localhost:11434

### For Production Deployment at repo.dare.co.zw

👉 **See: [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md)** for complete step-by-step instructions

## 📚 Documentation Guide

Choose based on your needs:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md)** | 🎯 **START HERE** - Complete deployment & integration checklist | 20 min |
| **[ROSERSG.md](./ROSERSG.md)** | Complete architecture, features, and API | 30 min |
| **[QUICKSTART.md](./QUICKSTART.md)** | Get running in minutes, basic usage | 10 min |
| **[EMBED_IN_DSPACE.md](./EMBED_IN_DSPACE.md)** | Full Angular component code for DSpace | 40 min |
| **[DSPACE_INTEGRATION.md](./DSPACE_INTEGRATION.md)** | Detailed 10-step integration guide | 25 min |
| **[DSPACE_API_REFERENCE.md](./DSPACE_API_REFERENCE.md)** | Complete API endpoint reference | 15 min |
| **[DEPLOY_DSPACE_LIVE.md](./DEPLOY_DSPACE_LIVE.md)** | Production deployment quick reference | 10 min |
| **[EMBEDDED_QUICK_START.md](./EMBEDDED_QUICK_START.md)** | 30-minute embedding guide | 15 min |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          DSpace Repository UI (Angular)         │
│          https://repo.dare.co.zw                │
├─────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐    │
│  │  Embedded rosersg Components            │    │
│  │  • Chat Widget (floating)               │    │
│  │  • Search Enhancement                  │    │
│  │  • Metadata Suggestions                │    │
│  │  • Recommendations                     │    │
│  └─────────────────────────────────────────┘    │
└────────────────┬────────────────────────────────┘
                 │
        Nginx Reverse Proxy
        /ai-api/ → :5000
        /ai/ → :3000
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼─────────────┐    ┌─────▼──────────────┐
│ rosersg API     │    │ rosersg Frontend   │
│ (Flask, :5000)  │    │ (React, :3000)    │
├─────────────────┤    ├────────────────────┤
│ • Chat Service  │    │ • Web UI           │
│ • Search Engine │    │ • Form Handling    │
│ • Metadata AI   │    │ • Result Display   │
│ • Recommendations│    │ • User Interface   │
└────────┬────────┘    └────────────────────┘
         │
    ┌────▼────────────────────┐
    │   Ollama LLM Engine      │
    │   (Port 11434)           │
    ├────────────────────────────┤
    │ • mistral (default)       │
    │ • neural-chat             │
    │ • nomic-embed-text        │
    │ • (add more as needed)    │
    └─────────────────────────────┘
```

## 🔑 Key Features

### 💬 Chat Assistant
- Ask questions about research in the repository
- Get context-aware responses using Ollama LLMs
- Conversation-aware interactions

### 🔍 Intelligent Search
- AI-enhanced query suggestions
- Semantic understanding of search terms
- Refined result recommendations

### 📝 Metadata Optimization
- Automatic metadata improvement suggestions
- Keyword extraction and enhancement
- Academic phrasing recommendations

### ⭐ Smart Recommendations
- Content-based recommendation engine
- Semantic similarity matching
- Discovery of related research

### 📊 Collection Analytics
- AI-generated collection insights
- Trend identification
- Popular topic analysis

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Ollama Configuration
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=mistral

# DSpace Configuration
DSPACE_ENDPOINT=https://repo.dare.co.zw

# API Security
ROSERSG_API_KEY=your-secure-api-key-here

# Flask Configuration
FLASK_ENV=production
DEBUG=false
```

### Configuration File (rosersg-config.json)

```json
{
  "ollama": {
    "endpoint": "http://localhost:11434",
    "model": "mistral",
    "temperature": 0.7,
    "context_length": 2048
  },
  "dspace": {
    "endpoint": "https://repo.dare.co.zw",
    "rest_api": "/server/api",
    "timeout": 30000
  }
}
```

## 📡 API Endpoints

### Core Endpoints (Require API Key)

- `POST /api/chat` - Chat with AI
- `POST /api/search/intelligent` - AI-enhanced search
- `POST /api/metadata/optimize` - Metadata suggestions
- `POST /api/recommendations` - Related items
- `GET /api/item/{id}/summarize` - Item summary
- `GET /api/collections/insights` - Collection analytics

### Public Endpoints

- `GET /health` - Health check
- `GET /api/status` - Detailed status

👉 See [DSPACE_API_REFERENCE.md](./DSPACE_API_REFERENCE.md) for complete API documentation

## 🐳 Docker Compose Services

### Services Included

1. **Ollama** (Port 11434)
   - LLM inference engine
   - Models: mistral, neural-chat, embeddings
   - Persistent volume for models

2. **rosersg API** (Port 5000)
   - Flask REST API
   - Health checks enabled
   - Depends on Ollama

3. **rosersg UI** (Port 3000)
   - React frontend
   - Development/standalone mode
   - Can be replaced with embedded DSpace components

## 🔧 Integration with DSpace 9

### Option 1: Embedded Components (Recommended)

Embed rosersg directly in your DSpace Angular theme:

1. Copy 4 Angular components to your DSpace installation
2. Update SharedModule with declarations
3. Add components to DSpace pages
4. Configure Nginx routing

👉 **Complete guide:** [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md)

### Option 2: Standalone UI

Access rosersg as separate application at `/ai/`:

- Works as independent tool
- No DSpace component changes needed
- Users navigate between DSpace and rosersg

### Option 3: Iframe Embedding

Embed rosersg UI in DSpace as iframe at `/ai/`:

- Quick integration
- Some CSS limitations
- Works with existing DSpace

## 📋 Deployment Steps (Summary)

### Phase 1: Backend Setup (5-10 min)
1. SSH to your server
2. Clone repository
3. Create .env file
4. Generate API key
5. Start Docker services
6. Pull Ollama models

### Phase 2: Nginx Routing (5 min)
1. Add proxy configuration to Nginx
2. Route `/ai-api/` to port 5000
3. Route `/ai/` to port 3000
4. Restart Nginx

### Phase 3: DSpace Integration (20-30 min)
1. Copy Angular components
2. Update SharedModule
3. Add components to pages
4. Configure environment
5. Build DSpace
6. Deploy

### Phase 4: Testing (5 min)
1. Verify API responds
2. Check chat works
3. Test search enhancement
4. Verify components appear

**Total Time: ~45-60 minutes**

## ✅ Deployment Checklist

- [ ] Backend services running (`docker compose ps`)
- [ ] API responding to health check
- [ ] Ollama models pulled
- [ ] Nginx routing configured
- [ ] rosersg components copied to DSpace
- [ ] SharedModule updated
- [ ] Components added to pages
- [ ] Environment configured
- [ ] DSpace built and deployed
- [ ] Chat button visible
- [ ] Search enhancement working
- [ ] Metadata suggestions visible
- [ ] Recommendations showing

## 🐛 Troubleshooting

### Backend Issues

**Ollama not healthy:**
```bash
docker logs rosersg-ollama
docker restart rosersg-ollama
# Wait 2+ minutes
docker compose ps
```

**API not responding:**
```bash
docker logs rosersg-api
curl http://localhost:5000/health
```

**DSpace not found:**
Check `.env` file - ensure `DSPACE_ENDPOINT=https://repo.dare.co.zw`

### Frontend Issues

**Components not displaying:**
- Check browser console for errors
- Verify SharedModule imports
- Check component files exist
- Rebuild DSpace

**Nginx 502 Bad Gateway:**
```bash
sudo nginx -t
sudo systemctl restart nginx
curl -v http://localhost:5000/health
```

See [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md) for more troubleshooting

## 🔐 Security

### API Key Management
- Generated with `openssl rand -hex 32`
- Store in `.env` file (not in git)
- Rotate regularly in production
- Use strong keys (32+ bytes)

### HTTPS/SSL
- Always use HTTPS in production
- Nginx handles SSL termination
- rosersg API uses HTTP internally

### CORS Configuration
- Configured in rosersg-config.json
- Restrict to trusted origins
- Set in Nginx reverse proxy

### Rate Limiting
- 100 requests/minute per API key
- Configurable in rosersg-config.json
- Prevents abuse

## 📊 Performance

### Optimization Tips
- **Smaller models**: Use neural-chat instead of mistral for faster responses
- **Caching**: Implement Redis for frequent queries
- **Batch processing**: Process multiple requests together
- **Load balancing**: Run multiple API instances

### Resource Requirements
- **Ollama**: 8GB+ RAM (varies by model)
- **API**: 2GB RAM, 1 CPU
- **Frontend**: Minimal (Node.js)
- **Disk**: 10GB+ for models

## 🚀 Advanced Usage

### Custom LLM Models

```bash
# SSH to server
docker compose exec ollama ollama pull llama2
docker compose exec ollama ollama pull openchat

# Update rosersg-config.json model selection
```

### Integration with DSpace Auth

Modify rosersg.py to validate DSpace user tokens:

```python
def verify_dspace_token(token):
    # Call DSpace auth API
    # Return user info if valid
```

### Semantic Embeddings

Enable advanced semantic search with embeddings:

```json
{
  "ollama": {
    "models": [
      {
        "name": "nomic-embed-text",
        "purpose": "embeddings",
        "enabled": true
      }
    ]
  }
}
```

## 📞 Support & Resources

### Documentation
- [ROSERSG.md](./ROSERSG.md) - Full documentation
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
- [DSPACE_API_REFERENCE.md](./DSPACE_API_REFERENCE.md) - API reference
- [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md) - Integration checklist

### GitHub
- Issues: https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-/issues
- Repository: https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-
- Branch: `claude/rosersg-ollama-dspace-ai-b9tvxu`

### Testing Endpoints

```bash
# Health check
curl https://repo.dare.co.zw/ai-api/health

# Status check (with API key)
API_KEY="your-key-here"
curl -H "X-API-Key: $API_KEY" \
  https://repo.dare.co.zw/ai-api/api/status
```

## 🎯 Getting Started

### New to rosersg? Start here:
1. Read [ROSERSG.md](./ROSERSG.md) for overview
2. Follow [QUICKSTART.md](./QUICKSTART.md) to get running
3. Check [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md) for production deployment

### Integrating with DSpace? Follow:
1. [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md) - Complete checklist
2. [EMBED_IN_DSPACE.md](./EMBED_IN_DSPACE.md) - Component code
3. [DSPACE_API_REFERENCE.md](./DSPACE_API_REFERENCE.md) - API reference

### Deploying to production?
1. [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md) - Phase 1-4
2. [DEPLOY_DSPACE_LIVE.md](./DEPLOY_DSPACE_LIVE.md) - Quick reference
3. [ROSERSG.md](./ROSERSG.md) - Advanced configuration

---

## 📄 License

Part of DARE Digital Repository - follows same license terms

## 🤖 Built with Love

Created to bring AI-powered knowledge discovery to digital repositories.

**rosersg: Powering Research Discovery with AI** 🚀

---

**Ready to integrate rosersg into your DSpace 9?**

👉 **Start with:** [DSPACE9_INTEGRATION_CHECKLIST.md](./DSPACE9_INTEGRATION_CHECKLIST.md)
