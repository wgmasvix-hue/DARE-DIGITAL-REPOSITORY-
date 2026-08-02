import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const API_KEY = process.env.REACT_APP_API_KEY || 'default-dev-key';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [searchQuery, setSearchQuery] = useState('');
  const [metadata, setMetadata] = useState({ title: '', description: '' });
  const [status, setStatus] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Status error:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`,
        { message: input },
        { headers: { 'X-API-Key': API_KEY } }
      );
      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIntelligentSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/search/intelligent`,
        { query: searchQuery },
        { headers: { 'X-API-Key': API_KEY } }
      );
      const assistantMessage = {
        role: 'assistant',
        content: `Search Results for "${searchQuery}":\n\n${response.data.ai_suggestions}`
      };
      setMessages([...messages, assistantMessage]);
      setSearchQuery('');
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeMetadata = async () => {
    if (!metadata.title.trim()) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/metadata/optimize`,
        { title: metadata.title, description: metadata.description },
        { headers: { 'X-API-Key': API_KEY } }
      );
      const assistantMessage = {
        role: 'assistant',
        content: `Metadata Suggestions for "${metadata.title}":\n\n${response.data.ai_suggestions}`
      };
      setMessages([...messages, assistantMessage]);
      setMetadata({ title: '', description: '' });
    } catch (error) {
      console.error('Metadata error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendations = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/recommendations`,
        { query: searchQuery },
        { headers: { 'X-API-Key': API_KEY } }
      );
      const assistantMessage = {
        role: 'assistant',
        content: `Recommendations for "${searchQuery}":\n\n${response.data.recommendations}`
      };
      setMessages([...messages, assistantMessage]);
      setSearchQuery('');
    } catch (error) {
      console.error('Recommendations error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">
          <div className="logo-icon">🤖</div>
          <h1>rosersg</h1>
          <p>AI for DSpace</p>
        </div>

        <nav className="tabs">
          <button
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            🔍 Search
          </button>
          <button
            className={`tab ${activeTab === 'metadata' ? 'active' : ''}`}
            onClick={() => setActiveTab('metadata')}
          >
            📝 Metadata
          </button>
          <button
            className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            ⭐ Recommendations
          </button>
        </nav>

        {status && (
          <div className="status-box">
            <h3>Status</h3>
            <div className="status-item">
              <span>Ollama:</span>
              <span className={`badge ${status.ollama_status === 'online' ? 'online' : 'offline'}`}>
                {status.ollama_status}
              </span>
            </div>
            <div className="status-item">
              <span>DSpace:</span>
              <span className="badge online">connected</span>
            </div>
          </div>
        )}
      </div>

      <div className="main">
        <div className="header">
          <h2>
            {activeTab === 'chat' && '💬 Chat with rosersg'}
            {activeTab === 'search' && '🔍 Intelligent Search'}
            {activeTab === 'metadata' && '📝 Metadata Optimizer'}
            {activeTab === 'recommendations' && '⭐ Smart Recommendations'}
          </h2>
        </div>

        <div className="content">
          {activeTab === 'chat' && (
            <>
              <div className="messages">
                {messages.length === 0 && (
                  <div className="welcome">
                    <div className="welcome-icon">🤖</div>
                    <h3>Welcome to rosersg</h3>
                    <p>I'm your AI assistant for the DARE Digital Repository.</p>
                    <p>Ask me anything about searching, discovering, or understanding academic research!</p>
                  </div>
                )}
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-area">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Ask me anything..."
                  disabled={loading}
                />
                <button onClick={sendMessage} disabled={loading} className="send-btn">
                  {loading ? '...' : '→'}
                </button>
              </div>
            </>
          )}

          {activeTab === 'search' && (
            <>
              <div className="messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-area">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="What are you looking for?"
                  disabled={loading}
                />
                <button onClick={handleIntelligentSearch} disabled={loading} className="search-btn">
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </>
          )}

          {activeTab === 'metadata' && (
            <>
              <div className="messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="form-area">
                <div className="form-group">
                  <label>Title</label>
                  <input
                    type="text"
                    value={metadata.title}
                    onChange={(e) => setMetadata({...metadata, title: e.target.value})}
                    placeholder="Item title"
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={metadata.description}
                    onChange={(e) => setMetadata({...metadata, description: e.target.value})}
                    placeholder="Item description (optional)"
                    rows="4"
                  />
                </div>
                <button onClick={handleOptimizeMetadata} disabled={loading} className="optimize-btn">
                  {loading ? 'Analyzing...' : 'Optimize'}
                </button>
              </div>
            </>
          )}

          {activeTab === 'recommendations' && (
            <>
              <div className="messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-area">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter a topic or item ID"
                  disabled={loading}
                />
                <button onClick={handleGetRecommendations} disabled={loading} className="recommend-btn">
                  {loading ? 'Analyzing...' : 'Recommend'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
