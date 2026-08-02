# rosersg - Ollama-Powered AI Assistant for DSpace

rosersg is an intelligent AI system that enhances the DARE Digital Repository (DSpace) with advanced AI capabilities powered by Ollama. It provides semantic search, metadata optimization, content summarization, recommendations, and an interactive AI assistant.

## Features

- **💬 Interactive Chat Interface**: Conversational AI assistant for exploring and understanding your repository
- **🔍 Intelligent Semantic Search**: AI-enhanced search with refined suggestions and results
- **📝 Metadata Optimization**: Automatic metadata improvement suggestions using LLMs
- **⭐ Smart Recommendations**: Discover related content using semantic similarity
- **📊 Collection Insights**: AI-generated insights about your digital collections
- **🎯 Content Summarization**: Generate concise summaries of repository items

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    rosersg Frontend (React)              │
│                    Port: 3000                            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              rosersg API Backend (Flask)                │
│              Port: 5000                                 │
│  - Chat & Conversation Management                      │
│  - Search Enhancement                                  │
│  - Metadata Optimization                               │
│  - Recommendation Engine                               │
│  - Collection Analytics                                │
└────────────┬─────────────────────────┬─────────────────┘
             │                         │
    ┌────────▼─────────┐    ┌─────────▼────────────┐
    │  Ollama LLM      │    │  DSpace Repository   │
    │  Port: 11434     │    │  API Integration     │
    │                  │    │                      │
    │ - mistral        │    │ - Search             │
    │ - neural-chat    │    │ - Metadata           │
    │ - embeddings     │    │ - Collections        │
    └──────────────────┘    └──────────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for UI development)
- Ollama installed and running (or Docker will handle it)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/wgmasvix-hue/dare-digital-repository-.git
cd dare-digital-repository-

# Copy environment template
cp .env.example .env

# Update API key in .env
nano .env  # Change ROSERSG_API_KEY to a secure value

# Start all services
docker-compose up -d

# Services will be available at:
# - Frontend: http://localhost:3000
# - API: http://localhost:5000
# - Ollama: http://localhost:11434
```

### Local Development Setup

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama serve

# In another terminal, pull a model
ollama pull mistral
ollama pull neural-chat
ollama pull nomic-embed-text

# Copy environment
cp .env.example .env

# Run the API server
python rosersg.py
```

#### Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Start development server
npm start

# Open browser to http://localhost:3000
```

## API Endpoints

### Health & Status

- `GET /health` - Service health check
- `GET /api/status` - Detailed system status

### Chat & Conversation

- `POST /api/chat` - Send message to AI assistant
  ```json
  {
    "message": "What research topics are in the repository?"
  }
  ```

### Search

- `POST /api/search/intelligent` - AI-enhanced search
  ```json
  {
    "query": "machine learning applications"
  }
  ```

### Metadata

- `POST /api/metadata/optimize` - Get metadata improvement suggestions
  ```json
  {
    "title": "A Study on Deep Learning",
    "description": "This study explores deep learning techniques"
  }
  ```

### Items

- `GET /api/item/{item_id}/summarize` - Generate item summary

### Recommendations

- `POST /api/recommendations` - Get related items
  ```json
  {
    "query": "neural networks",
    "item_id": "12345"
  }
  ```

### Collections

- `GET /api/collections/insights` - Get collection insights

### Authentication

All API endpoints (except `/health` and `/api/status`) require:
```
Header: X-API-Key: your-api-key
```

## Configuration

Edit `rosersg-config.json` to customize:

### Ollama Settings
- `endpoint`: Ollama server address
- `model`: Default LLM model (mistral, neural-chat, etc.)
- `temperature`: Response creativity (0.0 - 1.0)
- `context_length`: Maximum context window

### DSpace Settings
- `endpoint`: DSpace instance URL
- `rest_api`: REST API path
- `search_limit`: Default search result limit
- `timeout`: API timeout in milliseconds

### Features
Enable/disable individual features in the `rosersg_features` section

### Security
- Configure API key requirements
- Set rate limiting per IP
- Configure CORS allowed origins

## Environment Variables

Create `.env` file with:

```env
# Ollama
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=mistral

# DSpace
DSPACE_ENDPOINT=https://dspace.dare.co.zw

# API Security
ROSERSG_API_KEY=your-secure-key-here

# Flask
FLASK_ENV=production
DEBUG=false

# Logging
LOG_LEVEL=info
```

## Usage Examples

### Python Client

```python
import requests

API_URL = "http://localhost:5000"
API_KEY = "your-api-key"
headers = {"X-API-Key": API_KEY}

# Chat
response = requests.post(
    f"{API_URL}/api/chat",
    json={"message": "What are the latest research papers?"},
    headers=headers
)
print(response.json()["response"])

# Intelligent Search
response = requests.post(
    f"{API_URL}/api/search/intelligent",
    json={"query": "climate change"},
    headers=headers
)
print(response.json()["ai_suggestions"])

# Optimize Metadata
response = requests.post(
    f"{API_URL}/api/metadata/optimize",
    json={
        "title": "Climate Study",
        "description": "A research paper about climate"
    },
    headers=headers
)
print(response.json()["ai_suggestions"])
```

### JavaScript/Frontend

```javascript
const API_URL = 'http://localhost:5000';
const API_KEY = 'your-api-key';

// Chat
const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    message: 'Tell me about climate research'
  })
});

const data = await response.json();
console.log(data.response);
```

## Advanced Features

### Custom LLM Models

To use different Ollama models:

```bash
# Pull additional models
ollama pull llama2
ollama pull openchat
ollama pull zephyr

# Update rosersg-config.json model selection
# or set OLLAMA_MODEL environment variable
```

### Semantic Embeddings

rosersg uses `nomic-embed-text` for generating embeddings. Enable semantic search by configuring:

```json
{
  "ollama": {
    "models": [
      {
        "name": "nomic-embed-text",
        "purpose": "semantic embeddings",
        "embeddings": true
      }
    ]
  }
}
```

### Integration with DSpace Custom API

Extend DSpace integration by modifying `DSpaceClient` class in `rosersg.py`:

```python
def custom_search(self, filters):
    """Custom search with DSpace API"""
    url = f"{self.api_url}/discover/search"
    # Add custom filters
    params = {**filters}
    response = requests.get(url, params=params, timeout=30)
    return response.json()
```

## Deployment

### Production Deployment

```bash
# Build Docker image
docker build -t rosersg:latest .

# Run with production settings
docker run -d \
  --name rosersg \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e ROSERSG_API_KEY=your-secure-key \
  rosersg:latest
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (create if needed)

### Systemd Service

Create `/etc/systemd/system/rosersg.service`:

```ini
[Unit]
Description=rosersg AI Service
After=network.target

[Service]
Type=notify
User=rosersg
WorkingDirectory=/opt/rosersg
ExecStart=/opt/rosersg/venv/bin/python rosersg.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker restart rosersg-ollama
```

### API Errors
```bash
# Check API logs
docker logs rosersg-api

# Verify API key
curl -H "X-API-Key: your-key" http://localhost:5000/api/status
```

### DSpace Connection Issues
```bash
# Test DSpace connectivity
curl https://dspace.dare.co.zw/server/api/core/collections
```

## Performance Tuning

- **Batch Processing**: Adjust `search_limit` for optimal performance
- **Model Selection**: Smaller models (neural-chat) are faster but less capable
- **Caching**: Implement Redis for frequent queries
- **Load Balancing**: Use multiple API instances with load balancer

## Security Considerations

1. **API Keys**: Use strong, unique API keys in production
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Configure appropriate rate limits
4. **CORS**: Restrict CORS origins to trusted domains
5. **DSpace Auth**: Integrate with DSpace authentication if needed

## Contributing

To contribute to rosersg:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and test
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Submit a pull request

## License

This project is part of DARE Digital Repository and follows the same license terms.

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/wgmasvix-hue/dare-digital-repository-/issues
- Email: support@chengetai.com

## Roadmap

- [ ] Advanced semantic search with embeddings storage
- [ ] Multi-language support
- [ ] Custom fine-tuning for domain-specific tasks
- [ ] Real-time collection monitoring
- [ ] Integration with academic paper indexing
- [ ] Advanced analytics dashboard
- [ ] Batch metadata optimization
- [ ] Mobile application support

---

**Built with ❤️ for DARE Digital Repository**  
*Powering knowledge discovery with AI*
