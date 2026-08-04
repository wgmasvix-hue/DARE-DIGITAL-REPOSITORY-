# rosersg API Reference for DSpace 9 Integration

Complete API endpoint reference for DSpace Angular components integrating with rosersg.

## 🔌 Base Configuration

In your DSpace Angular environment files, set:

```typescript
// src/environments/environment.prod.ts
export const environment = {
  production: true,
  rosersg: {
    apiUrl: '/ai-api',        // Proxied through Nginx
    apiKey: 'YOUR_API_KEY'    // From rosersg .env file
  }
};
```

Or for development:
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  rosersg: {
    apiUrl: 'http://localhost:5000',  // Direct to rosersg backend
    apiKey: 'YOUR_API_KEY'
  }
};
```

---

## 💬 Chat Endpoint

**Endpoint:** `POST /api/chat`

### Request
```json
{
  "message": "What are the latest research papers about AI?"
}
```

### Response
```json
{
  "response": "The rosersg system found the following recent papers...",
  "model": "mistral",
  "timestamp": "2026-08-04T16:54:45Z"
}
```

### Usage in Component
```typescript
chatWithRosersg(message: string): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey,
    'Content-Type': 'application/json'
  });
  
  return this.http.post(`${this.apiUrl}/api/chat`, 
    { message }, 
    { headers }
  );
}
```

---

## 🔍 Intelligent Search Endpoint

**Endpoint:** `POST /api/search/intelligent`

### Request
```json
{
  "query": "machine learning applications",
  "limit": 10
}
```

### Response
```json
{
  "ai_suggestions": [
    "neural networks",
    "deep learning",
    "AI algorithms"
  ],
  "enhanced_query": "machine learning artificial intelligence applications neural networks",
  "original_query": "machine learning applications"
}
```

### Usage in Component
```typescript
enhanceSearchQuery(query: string): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey,
    'Content-Type': 'application/json'
  });
  
  return this.http.post(`${this.apiUrl}/api/search/intelligent`,
    { query, limit: 10 },
    { headers }
  );
}
```

---

## 📝 Metadata Optimization Endpoint

**Endpoint:** `POST /api/metadata/optimize`

### Request
```json
{
  "title": "Study of Deep Learning",
  "description": "This paper explores deep learning techniques and their applications",
  "subject": "Artificial Intelligence",
  "author": "Jane Doe"
}
```

### Response
```json
{
  "ai_suggestions": {
    "title": "Deep Learning Methodologies: A Comprehensive Study",
    "description": "This study provides comprehensive analysis of deep learning techniques...",
    "keywords": ["deep learning", "neural networks", "machine learning", "AI"],
    "improvements": [
      "Added more specific keywords",
      "Enhanced title with academic phrasing",
      "Expanded description for clarity"
    ]
  }
}
```

### Usage in Component
```typescript
optimizeMetadata(metadata: any): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey,
    'Content-Type': 'application/json'
  });
  
  return this.http.post(`${this.apiUrl}/api/metadata/optimize`,
    metadata,
    { headers }
  );
}
```

---

## ⭐ Recommendations Endpoint

**Endpoint:** `POST /api/recommendations`

### Request
```json
{
  "query": "neural networks",
  "item_id": "123e4567-e89b-12d3-a456-426614174000",
  "limit": 5
}
```

### Response
```json
{
  "recommendations": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "title": "Deep Learning Fundamentals",
      "similarity_score": 0.95,
      "author": "John Smith"
    },
    {
      "id": "323e4567-e89b-12d3-a456-426614174002",
      "title": "Machine Learning Applications",
      "similarity_score": 0.87,
      "author": "Jane Doe"
    }
  ],
  "query": "neural networks"
}
```

### Usage in Component
```typescript
getRecommendations(itemId: string, query: string): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey,
    'Content-Type': 'application/json'
  });
  
  return this.http.post(`${this.apiUrl}/api/recommendations`,
    { query, item_id: itemId, limit: 5 },
    { headers }
  );
}
```

---

## 📄 Item Summarization Endpoint

**Endpoint:** `GET /api/item/{item_id}/summarize`

### Request
```
GET /api/item/123e4567-e89b-12d3-a456-426614174000/summarize
```

### Response
```json
{
  "summary": "This research paper investigates deep learning methodologies...",
  "item_id": "123e4567-e89b-12d3-a456-426614174000",
  "original_length": 5000,
  "summary_length": 250
}
```

### Usage in Component
```typescript
summarizeItem(itemId: string): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey
  });
  
  return this.http.get(`${this.apiUrl}/api/item/${itemId}/summarize`,
    { headers }
  );
}
```

---

## 📊 Collection Insights Endpoint

**Endpoint:** `GET /api/collections/insights`

### Request
```
GET /api/collections/insights?collection_id=abc123
```

### Response
```json
{
  "collection_id": "abc123",
  "collection_name": "Computer Science",
  "total_items": 1547,
  "insights": {
    "top_topics": ["Machine Learning", "AI", "Data Science"],
    "recent_trends": ["Deep Learning", "Quantum Computing"],
    "popular_keywords": ["neural networks", "algorithms"]
  }
}
```

### Usage in Component
```typescript
getCollectionInsights(collectionId?: string): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey
  });
  
  const params = collectionId ? `?collection_id=${collectionId}` : '';
  return this.http.get(`${this.apiUrl}/api/collections/insights${params}`,
    { headers }
  );
}
```

---

## ✅ Health Check Endpoint

**Endpoint:** `GET /health`

### Response (No Auth Required)
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Usage in Component
```typescript
checkApiHealth(): Observable<any> {
  return this.http.get(`${this.apiUrl}/health`);
}
```

---

## 📊 Status Endpoint

**Endpoint:** `GET /api/status`

### Response
```json
{
  "status": "healthy",
  "services": {
    "ollama": "connected",
    "dspace": "connected"
  },
  "models": ["mistral", "neural-chat"],
  "api_version": "1.0.0"
}
```

### Usage in Component
```typescript
getApiStatus(): Observable<any> {
  const headers = new HttpHeaders({
    'X-API-Key': this.apiKey
  });
  
  return this.http.get(`${this.apiUrl}/api/status`,
    { headers }
  );
}
```

---

## 🔐 Authentication

All endpoints (except `/health`) require:

```http
Header: X-API-Key: YOUR_API_KEY
```

### TypeScript Service Example
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RosersqService {
  private apiUrl = environment.rosersg.apiUrl;
  private apiKey = environment.rosersg.apiKey;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'X-API-Key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  chat(message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/chat`,
      { message },
      { headers: this.getHeaders() }
    );
  }

  searchIntelligent(query: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/search/intelligent`,
      { query },
      { headers: this.getHeaders() }
    );
  }

  optimizeMetadata(metadata: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/metadata/optimize`,
      metadata,
      { headers: this.getHeaders() }
    );
  }

  getRecommendations(query: string, itemId?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/recommendations`,
      { query, item_id: itemId },
      { headers: this.getHeaders() }
    );
  }
}
```

---

## ⚙️ Error Handling

All endpoints return standard error responses:

```json
{
  "error": "Invalid query",
  "message": "Query parameter is required",
  "status": 400
}
```

### Example Error Handler
```typescript
chat(message: string): Observable<any> {
  return this.http.post(`${this.apiUrl}/api/chat`,
    { message },
    { headers: this.getHeaders() }
  ).pipe(
    catchError(error => {
      console.error('rosersg API error:', error);
      return throwError(() => new Error(error.error.message || 'API Error'));
    })
  );
}
```

---

## 🔧 Rate Limiting

- **Default Rate Limit**: 100 requests per minute per API key
- **Rate Limit Headers** (in response):
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1628094000

### Example
```typescript
handleRateLimit(response: HttpResponse<any>) {
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  
  if (parseInt(remaining) < 10) {
    console.warn('Approaching rate limit. Resets at:', new Date(parseInt(reset) * 1000));
  }
}
```

---

## 📍 Endpoint Availability

| Endpoint | Dev | Production | Notes |
|----------|-----|------------|----|
| `/health` | ✅ | ✅ | No auth required |
| `/api/status` | ✅ | ✅ | Requires API key |
| `/api/chat` | ✅ | ✅ | Streaming not supported |
| `/api/search/intelligent` | ✅ | ✅ | Used by search component |
| `/api/metadata/optimize` | ✅ | ✅ | For metadata suggestions |
| `/api/recommendations` | ✅ | ✅ | Requires item_id or query |
| `/api/item/{id}/summarize` | ✅ | ✅ | Optional for item pages |
| `/api/collections/insights` | ✅ | ✅ | For dashboard analytics |

---

## 🚀 Quick Integration Template

Copy this to your rosersg service:

```typescript
// rosersg.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class RosersqService {
  private apiUrl = environment.rosersg.apiUrl;
  private apiKey = environment.rosersg.apiKey;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'X-API-Key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  chat(message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/chat`,
      { message }, { headers: this.getHeaders() }
    ).pipe(catchError(this.handleError));
  }

  searchIntelligent(query: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/search/intelligent`,
      { query }, { headers: this.getHeaders() }
    ).pipe(catchError(this.handleError));
  }

  optimizeMetadata(metadata: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/metadata/optimize`,
      metadata, { headers: this.getHeaders() }
    ).pipe(catchError(this.handleError));
  }

  getRecommendations(query: string, itemId?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/recommendations`,
      { query, item_id: itemId }, { headers: this.getHeaders() }
    ).pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('rosersg API error:', error);
    return throwError(() => new Error(error.error?.message || 'API Error'));
  }
}
```

---

## 📞 Testing API Endpoints

### Using cURL

```bash
# Set your API key
API_KEY="your-api-key-here"
API_URL="https://repo.dare.co.zw/ai-api"

# Test health (no auth)
curl $API_URL/health

# Test status
curl -H "X-API-Key: $API_KEY" $API_URL/api/status

# Test chat
curl -X POST $API_URL/api/chat \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello rosersg!"}'

# Test search
curl -X POST $API_URL/api/search/intelligent \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'

# Test metadata optimization
curl -X POST $API_URL/api/metadata/optimize \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Study", "description": "Research on artificial intelligence"}'

# Test recommendations
curl -X POST $API_URL/api/recommendations \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "neural networks"}'
```

---

## 🎯 Common Integration Patterns

### Pattern 1: Chat in Modal
```typescript
openChat(initialMessage?: string) {
  this.rosersq.chat(initialMessage || 'Hello!').subscribe(
    response => this.displayChatResponse(response.response),
    error => this.showError(error)
  );
}
```

### Pattern 2: Search Enhancement
```typescript
performSearch(query: string) {
  this.rosersq.searchIntelligent(query).subscribe(
    response => this.showEnhancedResults(response.ai_suggestions),
    error => this.fallbackToBasicSearch(query)
  );
}
```

### Pattern 3: Metadata Suggestions on Item Page
```typescript
ngOnInit() {
  this.rosersq.optimizeMetadata(this.item.metadata).subscribe(
    response => this.metadataSuggestions = response.ai_suggestions,
    error => console.error(error)
  );
}
```

### Pattern 4: Related Items on Item Page
```typescript
loadRecommendations() {
  this.rosersq.getRecommendations(this.item.title, this.item.id).subscribe(
    response => this.relatedItems = response.recommendations,
    error => console.error(error)
  );
}
```

---

**✅ Ready to integrate? Reference these endpoints in your DSpace components!**
