# Embedding rosersg in DSpace UI

Complete guide to integrate rosersg AI directly into the DSpace Angular interface for seamless UX.

## 🎯 Embedding Options

### Option 1: Embedded Components (Recommended)
Add rosersg widgets directly to DSpace pages:
- AI chat in search results
- Smart search bar enhancement
- AI suggestions on item detail pages
- Recommendations sidebar

### Option 2: Full Theme Integration
Replace/enhance entire DSpace theme with rosersg:
- Custom search page with AI
- Item page with AI metadata display
- Collections with AI insights

## 📁 Project Structure

Assuming you have DSpace Angular at `/opt/dspace-angular`:

```
/opt/dspace-angular/
├── src/
│   └── app/
│       ├── shared/
│       │   └── components/
│       │       ├── rosersg-chat/
│       │       ├── rosersg-search-enhance/
│       │       ├── rosersg-metadata-suggestions/
│       │       └── rosersg-recommendations/
│       ├── item-page/
│       │   └── item-detail.component.ts  (modify)
│       └── search-page/
│           └── search.component.ts  (modify)
```

## 🔧 Part 1: Create Embedded Components

### 1.1 Create rosersg Chat Component

**File:** `src/app/shared/components/rosersg-chat/rosersg-chat.component.ts`

```typescript
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-rosersg-chat',
  templateUrl: './rosersg-chat.component.html',
  styleUrls: ['./rosersg-chat.component.scss']
})
export class RosersqChatComponent implements OnInit {
  @Input() placeholder = 'Ask rosersg about this item...';
  @Input() context: string = '';  // Item ID or search query
  
  messages: ChatMessage[] = [];
  inputText = '';
  loading = false;
  isOpen = false;

  private apiUrl = '/ai-api';
  private apiKey = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // Get API key from localStorage (set during login)
    this.apiKey = localStorage.getItem('rosersg-api-key') || '';
    if (!this.apiKey) {
      this.apiKey = (window as any).ROSERSG_API_KEY || '';
    }
  }

  sendMessage() {
    if (!this.inputText.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: this.inputText
    };
    this.messages.push(userMessage);
    this.loading = true;

    const message = this.inputText;
    this.inputText = '';

    this.http.post<any>(
      `${this.apiUrl}/api/chat`,
      { message: message + (this.context ? ` (Context: ${this.context})` : '') },
      { headers: { 'X-API-Key': this.apiKey } }
    ).subscribe(
      (response) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.response
        };
        this.messages.push(assistantMessage);
        this.loading = false;
      },
      (error) => {
        console.error('Chat error:', error);
        this.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        });
        this.loading = false;
      }
    );
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
  }
}
```

**File:** `src/app/shared/components/rosersg-chat/rosersg-chat.component.html`

```html
<div class="rosersg-chat">
  <!-- Chat Toggle Button -->
  <button 
    class="chat-toggle" 
    (click)="toggleChat()"
    [class.open]="isOpen"
    title="Ask rosersg AI"
  >
    🤖
  </button>

  <!-- Chat Panel -->
  <div class="chat-panel" *ngIf="isOpen">
    <div class="chat-header">
      <h3>rosersg AI Assistant</h3>
      <button class="close-btn" (click)="toggleChat()">✕</button>
    </div>

    <div class="chat-messages">
      <div class="empty-state" *ngIf="messages.length === 0">
        <p>Ask me anything about this research</p>
      </div>

      <div 
        *ngFor="let msg of messages" 
        [class]="'message ' + msg.role"
      >
        {{ msg.content }}
      </div>

      <div class="loading" *ngIf="loading">
        <span>rosersg is thinking...</span>
      </div>
    </div>

    <div class="chat-input">
      <input
        [(ngModel)]="inputText"
        [placeholder]="placeholder"
        (keyup.enter)="sendMessage()"
        [disabled]="loading"
        type="text"
      />
      <button 
        (click)="sendMessage()" 
        [disabled]="loading || !inputText.trim()"
        class="send-btn"
      >
        ↑
      </button>
    </div>
  </div>
</div>
```

**File:** `src/app/shared/components/rosersg-chat/rosersg-chat.component.scss`

```scss
.rosersg-chat {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;

  .chat-toggle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-size: 28px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    transition: transform 0.3s, box-shadow 0.3s;

    &:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    &.open {
      display: none;
    }
  }

  .chat-panel {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 380px;
    height: 500px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    animation: slideUp 0.3s ease;

    @media (max-width: 480px) {
      width: calc(100vw - 40px);
      height: 60vh;
      bottom: 0;
      right: 0;
      left: 0;
      border-radius: 12px 12px 0 0;
    }
  }

  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px 12px 0 0;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 20px;
      cursor: pointer;
      padding: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        opacity: 0.8;
      }
    }
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #999;
      font-size: 14px;
    }

    .message {
      display: flex;
      margin-bottom: 8px;
      word-wrap: break-word;
      font-size: 14px;
      line-height: 1.4;

      &.user {
        justify-content: flex-end;

        {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 10px 14px;
          border-radius: 12px 12px 4px 12px;
        }
      }

      &.assistant {
        justify-content: flex-start;

        {
          background: #f0f0f0;
          color: #333;
          padding: 10px 14px;
          border-radius: 12px 12px 12px 4px;
        }
      }
    }

    .loading {
      display: flex;
      justify-content: flex-start;
      padding: 8px 0;

      span {
        color: #999;
        font-size: 13px;
        font-style: italic;
      }
    }
  }

  .chat-input {
    display: flex;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid #eee;
    background: white;
    border-radius: 0 0 12px 12px;

    input {
      flex: 1;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 14px;
      font-family: inherit;

      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }

      &:disabled {
        background: #f5f5f5;
        color: #999;
      }
    }

    .send-btn {
      width: 36px;
      height: 36px;
      border: none;
      border-radius: 8px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      cursor: pointer;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s;

      &:hover:not(:disabled) {
        transform: scale(1.05);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 1.2 Create Smart Search Component

**File:** `src/app/shared/components/rosersg-search-enhance/rosersg-search-enhance.component.ts`

```typescript
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-rosersg-search-enhance',
  templateUrl: './rosersg-search-enhance.component.html',
  styleUrls: ['./rosersg-search-enhance.component.scss']
})
export class RosersqSearchEnhanceComponent {
  @Input() query = '';
  @Output() enhancedQuery = new EventEmitter<string>();

  suggestions: string[] = [];
  loading = false;
  showSuggestions = false;

  private apiUrl = '/ai-api';
  private apiKey = '';

  constructor(private http: HttpClient) {}

  enhanceSearch() {
    if (!this.query.trim()) return;

    this.loading = true;
    this.apiKey = localStorage.getItem('rosersg-api-key') || '';

    this.http.post<any>(
      `${this.apiUrl}/api/search/intelligent`,
      { query: this.query },
      { headers: { 'X-API-Key': this.apiKey } }
    ).subscribe(
      (response) => {
        // Parse suggestions from response
        this.suggestions = response.ai_suggestions
          .split('\n')
          .filter(s => s.trim())
          .slice(0, 3);
        this.showSuggestions = true;
        this.loading = false;
      },
      (error) => {
        console.error('Search enhancement error:', error);
        this.loading = false;
      }
    );
  }

  selectSuggestion(suggestion: string) {
    this.query = suggestion;
    this.showSuggestions = false;
    this.enhancedQuery.emit(suggestion);
  }
}
```

**File:** `src/app/shared/components/rosersg-search-enhance/rosersg-search-enhance.component.html`

```html
<div class="search-enhance">
  <div class="search-box">
    <input
      [(ngModel)]="query"
      placeholder="Search with AI assistance..."
      (focus)="enhanceSearch()"
      (keyup.enter)="enhancedQuery.emit(query)"
      type="text"
    />
    <button (click)="enhanceSearch()" [disabled]="loading" class="enhance-btn">
      <span *ngIf="!loading">✨ AI</span>
      <span *ngIf="loading">⏳</span>
    </button>
  </div>

  <div class="suggestions" *ngIf="showSuggestions && suggestions.length">
    <div class="suggestion-label">AI Suggestions:</div>
    <button
      *ngFor="let suggestion of suggestions"
      (click)="selectSuggestion(suggestion)"
      class="suggestion-item"
    >
      {{ suggestion }}
    </button>
  </div>
</div>
```

**File:** `src/app/shared/components/rosersg-search-enhance/rosersg-search-enhance.component.scss`

```scss
.search-enhance {
  width: 100%;

  .search-box {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;

    input {
      flex: 1;
      padding: 12px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 14px;

      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }

    .enhance-btn {
      padding: 12px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      transition: transform 0.2s;

      &:hover:not(:disabled) {
        transform: scale(1.05);
      }

      &:disabled {
        opacity: 0.6;
      }
    }
  }

  .suggestions {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid #667eea;

    .suggestion-label {
      font-size: 12px;
      font-weight: 600;
      color: #667eea;
      margin-bottom: 8px;
      text-transform: uppercase;
    }

    .suggestion-item {
      display: block;
      width: 100%;
      padding: 8px;
      margin-bottom: 4px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 4px;
      text-align: left;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.2s;

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        background: #667eea;
        color: white;
        border-color: #667eea;
      }
    }
  }
}
```

### 1.3 Create Metadata Suggestions Component

**File:** `src/app/shared/components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component.ts`

```typescript
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-rosersg-metadata-suggestions',
  templateUrl: './rosersg-metadata-suggestions.component.html',
  styleUrls: ['./rosersg-metadata-suggestions.component.scss']
})
export class RosersqMetadataSuggestionsComponent implements OnInit {
  @Input() itemTitle: string = '';
  @Input() itemDescription: string = '';

  suggestions: string = '';
  loading = false;
  expanded = false;

  private apiUrl = '/ai-api';
  private apiKey = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.apiKey = localStorage.getItem('rosersg-api-key') || '';
    if (this.itemTitle) {
      this.getSuggestions();
    }
  }

  getSuggestions() {
    if (!this.itemTitle.trim()) return;

    this.loading = true;

    this.http.post<any>(
      `${this.apiUrl}/api/metadata/optimize`,
      {
        title: this.itemTitle,
        description: this.itemDescription
      },
      { headers: { 'X-API-Key': this.apiKey } }
    ).subscribe(
      (response) => {
        this.suggestions = response.ai_suggestions;
        this.loading = false;
      },
      (error) => {
        console.error('Metadata suggestions error:', error);
        this.loading = false;
      }
    );
  }

  toggleExpanded() {
    this.expanded = !this.expanded;
  }
}
```

**File:** `src/app/shared/components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component.html`

```html
<div class="metadata-suggestions">
  <button 
    class="toggle-btn"
    (click)="toggleExpanded()"
  >
    <span *ngIf="!expanded">▼</span>
    <span *ngIf="expanded">▲</span>
    🤖 AI Metadata Suggestions
  </button>

  <div class="suggestions-content" *ngIf="expanded">
    <div class="loading" *ngIf="loading">
      <p>Analyzing metadata...</p>
    </div>

    <div class="suggestions-text" *ngIf="!loading && suggestions">
      {{ suggestions }}
    </div>

    <div class="no-suggestions" *ngIf="!loading && !suggestions">
      <p>No suggestions available</p>
    </div>
  </div>
</div>
```

**File:** `src/app/shared/components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component.scss`

```scss
.metadata-suggestions {
  margin: 16px 0;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;

  .toggle-btn {
    width: 100%;
    padding: 12px 16px;
    background: #f8f9fa;
    border: none;
    text-align: left;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: #667eea;
    display: flex;
    align-items: center;
    gap: 8px;
    border-radius: 8px;
    transition: background 0.2s;

    &:hover {
      background: #f0f0f0;
    }

    span:first-child {
      font-size: 12px;
    }
  }

  .suggestions-content {
    padding: 12px 16px;
    border-top: 1px solid #e0e0e0;

    .loading,
    .no-suggestions {
      color: #999;
      font-size: 14px;
      text-align: center;
      padding: 8px 0;
    }

    .suggestions-text {
      color: #333;
      font-size: 14px;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}
```

### 1.4 Create Recommendations Component

**File:** `src/app/shared/components/rosersg-recommendations/rosersg-recommendations.component.ts`

```typescript
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Recommendation {
  id: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-rosersg-recommendations',
  templateUrl: './rosersg-recommendations.component.html',
  styleUrls: ['./rosersg-recommendations.component.scss']
})
export class RosersqRecommendationsComponent implements OnInit {
  @Input() itemId: string = '';
  @Input() searchQuery: string = '';

  recommendations: Recommendation[] = [];
  loading = false;
  analysis: string = '';

  private apiUrl = '/ai-api';
  private apiKey = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.apiKey = localStorage.getItem('rosersg-api-key') || '';
    if (this.itemId || this.searchQuery) {
      this.getRecommendations();
    }
  }

  getRecommendations() {
    this.loading = true;

    this.http.post<any>(
      `${this.apiUrl}/api/recommendations`,
      {
        item_id: this.itemId,
        query: this.searchQuery
      },
      { headers: { 'X-API-Key': this.apiKey } }
    ).subscribe(
      (response) => {
        this.analysis = response.recommendations;
        // Parse search results into recommendations
        if (response.search_results?.page?.content) {
          this.recommendations = response.search_results.page.content.map((item: any) => ({
            id: item.uuid || item.id,
            title: item.name || 'Untitled',
            description: item.metadata?.description?.join(', ') || ''
          }));
        }
        this.loading = false;
      },
      (error) => {
        console.error('Recommendations error:', error);
        this.loading = false;
      }
    );
  }
}
```

**File:** `src/app/shared/components/rosersg-recommendations/rosersg-recommendations.component.html`

```html
<div class="recommendations">
  <h3>🤖 AI-Powered Recommendations</h3>

  <div class="loading" *ngIf="loading">
    <p>Finding related research...</p>
  </div>

  <div class="analysis" *ngIf="analysis && !loading">
    <p>{{ analysis }}</p>
  </div>

  <div class="recommendation-list" *ngIf="recommendations.length">
    <h4>Related Items:</h4>
    <div *ngFor="let rec of recommendations" class="recommendation-item">
      <a [href]="'/items/' + rec.id">
        <h5>{{ rec.title }}</h5>
        <p>{{ rec.description | slice:0:100 }}...</p>
      </a>
    </div>
  </div>
</div>
```

**File:** `src/app/shared/components/rosersg-recommendations/rosersg-recommendations.component.scss`

```scss
.recommendations {
  margin: 20px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;

  h3 {
    margin: 0 0 12px 0;
    color: #667eea;
    font-size: 16px;
  }

  .loading {
    text-align: center;
    color: #999;
    padding: 12px 0;
  }

  .analysis {
    background: white;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 12px;
    font-size: 14px;
    line-height: 1.6;

    p {
      margin: 0;
    }
  }

  .recommendation-list {
    h4 {
      font-size: 13px;
      color: #667eea;
      margin: 0 0 8px 0;
      text-transform: uppercase;
    }

    .recommendation-item {
      background: white;
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 8px;
      border-left: 3px solid #764ba2;
      transition: transform 0.2s;

      &:hover {
        transform: translateX(4px);
      }

      a {
        text-decoration: none;
        color: inherit;
      }

      h5 {
        margin: 0 0 4px 0;
        font-size: 14px;
        color: #333;
        font-weight: 600;

        &:hover {
          color: #667eea;
        }
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #666;
      }
    }
  }
}
```

## 🔗 Part 2: Integrate into DSpace Pages

### 2.1 Add Chat to Item Detail Page

**File:** `src/app/item-page/full/item-detail.component.ts` (modify existing)

```typescript
// Add to your existing component

export class ItemDetailComponent {
  item$: Observable<Item>;
  itemId: string;

  constructor(
    private route: ActivatedRoute,
    // ... other injections
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.itemId = params['id'];
    });

    this.item$ = this.getItem();
  }
}
```

**File:** `src/app/item-page/full/item-detail.component.html` (modify existing)

```html
<!-- Add rosersg components to item page -->

<div class="item-detail">
  <!-- Existing DSpace content -->
  
  <!-- Add rosersg chat -->
  <app-rosersg-chat 
    [context]="itemId"
    placeholder="Ask about this research..."
  ></app-rosersg-chat>

  <!-- Add AI metadata suggestions -->
  <app-rosersg-metadata-suggestions
    [itemTitle]="(item$ | async)?.name"
    [itemDescription]="(item$ | async)?.metadata?.['dc.description.abstract']?.[0]?.value"
  ></app-rosersg-metadata-suggestions>

  <!-- Add AI recommendations -->
  <app-rosersg-recommendations
    [itemId]="itemId"
    [searchQuery]="(item$ | async)?.name"
  ></app-rosersg-recommendations>
</div>
```

### 2.2 Add Smart Search to Search Page

**File:** `src/app/search-page/search.component.html` (modify existing)

```html
<!-- Add rosersg smart search to search bar -->

<div class="search-container">
  <!-- Existing search UI -->
  
  <!-- Add rosersg enhanced search -->
  <app-rosersg-search-enhance
    [(ngModel)]="query"
    (enhancedQuery)="search($event)"
  ></app-rosersg-search-enhance>
</div>

<!-- Search results with rosersg chat -->
<div class="search-results">
  <!-- Existing results -->
  
  <!-- Add chat for results context -->
  <app-rosersg-chat
    [context]="query"
    placeholder="Ask about these search results..."
  ></app-rosersg-chat>
</div>
```

### 2.3 Add to Module Declarations

**File:** `src/app/shared/shared.module.ts`

```typescript
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

// Import rosersg components
import { RosersqChatComponent } from './components/rosersg-chat/rosersg-chat.component';
import { RosersqSearchEnhanceComponent } from './components/rosersg-search-enhance/rosersg-search-enhance.component';
import { RosersqMetadataSuggestionsComponent } from './components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component';
import { RosersqRecommendationsComponent } from './components/rosersg-recommendations/rosersg-recommendations.component';

@NgModule({
  declarations: [
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent
  ],
  imports: [
    CommonModule,
    HttpClientModule,
    FormsModule
  ],
  exports: [
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent
  ]
})
export class SharedModule { }
```

## 🔒 Part 3: Setup API Access in DSpace

### 3.1 Environment Configuration

**File:** `src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  // ... other config
  rosersg: {
    apiUrl: '/ai-api',  // Via Nginx reverse proxy
    enabled: true
  }
};
```

### 3.2 Add API Key to DSpace Theme

Add to your DSpace HTML head or theme initialization:

```html
<script>
  // Set rosersg API key from DSpace config or user session
  window.ROSERSG_API_KEY = 'your-api-key-here';
  
  // Or get from localStorage after user login
  if (localStorage.getItem('auth_token')) {
    // Fetch API key from your auth service
    localStorage.setItem('rosersg-api-key', 'your-user-api-key');
  }
</script>
```

## 🌐 Part 4: Nginx Configuration

Update your Nginx config to route API calls:

```nginx
# In your /etc/nginx/sites-enabled/repo.dare.co.zw

server {
    listen 443 ssl http2;
    server_name repo.dare.co.zw;

    # ... existing SSL config ...

    # Route DSpace Angular app
    location / {
        proxy_pass http://localhost:4200/;  # DSpace Angular dev/prod
    }

    # Route rosersg API
    location /ai-api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route DSpace REST API (if not at root)
    location /server/api/ {
        proxy_pass http://localhost:8080/server/api/;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

## 📦 Building DSpace with Embedded rosersg

```bash
# 1. Navigate to DSpace Angular
cd /opt/dspace-angular

# 2. Install npm dependencies
npm install

# 3. Add components (done above)

# 4. Build for production
ng build --prod

# 5. Serve via Nginx or Java backend
```

## ✅ Verification Checklist

- [ ] All 4 rosersg components created
- [ ] Components added to SharedModule
- [ ] Components integrated into item detail page
- [ ] Components integrated into search page  
- [ ] Nginx configured with /ai-api/ route
- [ ] rosersg API running on port 5000
- [ ] API key accessible to Angular app
- [ ] DSpace built and running
- [ ] Can see chat button on pages
- [ ] Can click chat and send messages
- [ ] Can use smart search
- [ ] Can see metadata suggestions
- [ ] Can see recommendations

## 🎯 Result

Users now see:

✅ **Chat button** (floating) on every page
✅ **AI suggestions** for search
✅ **Metadata improvements** on item pages
✅ **Related items** recommendations
✅ **Seamless integration** - no separate app needed

## 🚀 Advanced: Custom Styling

Customize the look to match your DSpace theme:

```scss
// Override in your theme styles
.rosersg-chat .chat-panel {
  background: var(--theme-bg-color);
  border: 1px solid var(--theme-border-color);
}

.rosersg-chat .chat-toggle {
  background: linear-gradient(135deg, var(--theme-primary), var(--theme-secondary));
}
```

## 📚 Component Reference

| Component | Purpose | Location |
|-----------|---------|----------|
| rosersg-chat | Floating AI chat | Any page |
| rosersg-search-enhance | Smart search suggestions | Search page |
| rosersg-metadata-suggestions | Metadata improvements | Item detail |
| rosersg-recommendations | Related items AI | Item detail, search |

---

**Result: rosersg seamlessly embedded in DSpace!** 🎉
