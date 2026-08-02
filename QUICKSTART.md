# rosersg Quick Start Guide

Get rosersg up and running in minutes!

## 🚀 Fastest Setup (30 seconds)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Start everything
docker-compose up -d

# Wait 30-60 seconds for services to initialize...

# Open in browser
# http://localhost:3000
```

## ✅ Verify Installation

```bash
# Check services are running
docker-compose ps

# Test API health
curl http://localhost:5000/health

# Test with API key
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" http://localhost:5000/api/status
```

## 💬 Try Your First Chat

### Via Web UI
1. Open http://localhost:3000
2. Click "Chat" tab
3. Type: "What is a digital repository?"
4. Click send or press Enter

### Via API
```bash
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)

curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"message": "What can you help me with?"}'
```

## 🔍 Try Intelligent Search

### Via Web UI
1. Click "Search" tab
2. Type: "machine learning"
3. Click "Search"
4. See AI-enhanced suggestions

### Via API
```bash
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)

curl -X POST http://localhost:5000/api/search/intelligent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"query": "machine learning applications"}'
```

## 📝 Try Metadata Optimization

### Via Web UI
1. Click "Metadata" tab
2. Enter Title: "Study of Neural Networks"
3. Enter Description: "Research on deep learning"
4. Click "Optimize"
5. See AI suggestions

### Via API
```bash
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)

curl -X POST http://localhost:5000/api/metadata/optimize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "title": "Study of Neural Networks",
    "description": "Research on deep learning techniques"
  }'
```

## ⭐ Get Recommendations

### Via Web UI
1. Click "Recommendations" tab
2. Type topic: "artificial intelligence"
3. Click "Recommend"
4. See AI-powered suggestions

### Via API
```bash
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)

curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"query": "artificial intelligence"}'
```

## 🛑 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful - removes data!)
docker-compose down -v
```

## 📋 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web UI |
| API | http://localhost:5000 | REST API |
| Ollama | http://localhost:11434 | LLM Engine |
| API Docs | http://localhost:5000/api/status | Status Check |

## 🔑 API Key

Your API key is in `.env` file. It's used for all API requests:

```bash
# View your API key
grep ROSERSG_API_KEY .env
```

Use in requests:
```bash
curl -H "X-API-Key: YOUR_KEY_HERE" http://localhost:5000/api/status
```

## 📚 Available LLM Models

rosersg comes with support for:

- **mistral** - General-purpose reasoning (default)
- **neural-chat** - Conversational AI
- **nomic-embed-text** - Semantic embeddings

Switch models by updating `.env`:
```bash
OLLAMA_MODEL=neural-chat
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs -f

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Ollama connection error
```bash
# Check Ollama is ready
docker logs rosersg-ollama

# Wait a moment and retry - Ollama needs time to start
```

### UI not loading
```bash
# Check if port 3000 is in use
lsof -i :3000

# Check UI logs
docker-compose logs rosersg-ui
```

### API not responding
```bash
# Check API logs
docker-compose logs rosersg-api

# Verify network
docker-compose exec rosersg-api ping ollama
```

## 📖 Learn More

- Full documentation: [ROSERSG.md](./ROSERSG.md)
- GitHub: https://github.com/wgmasvix-hue/dare-digital-repository-
- DARE Project: https://dspace.dare.co.zw

## 🎓 Example Workflows

### Workflow 1: Explore Research Topics
```
1. Go to Chat tab
2. Ask: "What are recent trends in AI research?"
3. Ask: "Tell me about reinforcement learning"
4. Switch to Search tab
5. Search for "reinforcement learning"
6. Review recommendations
```

### Workflow 2: Improve Metadata
```
1. Go to Metadata tab
2. Paste incomplete metadata
3. Get AI suggestions
4. Apply improvements to your DSpace instance
5. Run optimization again for verification
```

### Workflow 3: Discover Related Research
```
1. Go to Recommendations tab
2. Enter your research topic
3. Review suggested items
4. Click items to learn more
5. Export or save recommendations
```

## 🚀 Next Steps

1. **Customize Configuration**
   - Edit `rosersg-config.json`
   - Update `.env` with your values
   - Restart services: `docker-compose restart`

2. **Integrate with DSpace**
   - Update `DSPACE_ENDPOINT` in `.env`
   - Restart API: `docker-compose restart rosersg-api`

3. **Deploy to Production**
   - See ROSERSG.md > Deployment section
   - Use environment-specific `.env` files
   - Configure HTTPS and security

4. **Extend Capabilities**
   - Add custom endpoints to `rosersg.py`
   - Create custom UI components
   - Integrate with additional services

---

Happy exploring with rosersg! 🎉
