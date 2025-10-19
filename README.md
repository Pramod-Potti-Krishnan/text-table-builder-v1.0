# Text and Table Content Builder v1.0

LLM-powered content generation microservice for presentation slides. Generates rich HTML text and tables with context retention and word count control.

## 🚀 Features

- **Rich HTML Text Generation**
  - Semantic HTML with proper tags (p, ul, ol, strong, em, mark, etc.)
  - Word count control with ±10% tolerance
  - Context-aware content that flows from previous slides
  - Professional formatting with emphasis and highlights

- **Smart Table Generation**
  - LLM-optimized table structures
  - Automatic data analysis and column selection
  - Rich formatting (numeric alignment, growth indicators, totals)
  - Flexible data input (JSON, descriptions)

- **Context Retention**
  - Session-based presentation tracking
  - Maintains slide history for content flow
  - Coherent narrative across slides
  - Configurable context window (default: 5 slides)

- **Multi-Provider LLM Support**
  - Google Gemini (default: gemini-2.0-flash-exp)
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
  - Easy provider switching via environment variables

- **Production-Ready**
  - FastAPI with async support
  - Railway deployment configuration
  - Redis support for distributed sessions
  - Comprehensive logging and error handling
  - API documentation with Swagger UI

---

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [System Prompts](#system-prompts)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Installation

### Prerequisites

- Python 3.9+
- pip or conda
- Google API Key (for Gemini) or OpenAI/Anthropic API key

### Local Installation

```bash
# Clone the repository
cd text_table_builder/v1.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# At minimum, set GOOGLE_API_KEY for Gemini
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# LLM Provider Configuration
LLM_PROVIDER=gemini  # Options: gemini, openai, anthropic
LLM_MODEL=gemini-2.0-flash-exp  # Provider-specific model
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# API Keys (set the one for your provider)
GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Session Management
SESSION_CACHE_TTL=3600  # 1 hour
SESSION_MAX_HISTORY=5   # Max slides in context
USE_REDIS=false         # Set to true for distributed sessions

# Word Count Configuration
WORD_COUNT_TOLERANCE=0.10  # ±10% variance allowed

# Server Configuration
PORT=8001
HOST=0.0.0.0
LOG_LEVEL=info
```

### Configuring LLM Providers

#### Gemini (Default)
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
GOOGLE_API_KEY=your_key_here
```

#### OpenAI
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your_key_here
```

#### Anthropic
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your_key_here
```

---

## 🚀 Quick Start

### Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python main.py
```

The server will start on `http://localhost:8001`.

### Access API Documentation

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Test Health Endpoint

```bash
curl http://localhost:8001/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "text-table-builder",
  "llm_provider": "gemini",
  "llm_model": "gemini-2.0-flash-exp"
}
```

---

## 📚 API Documentation

### Base URL

- Local: `http://localhost:8001/api/v1`
- Production: `https://your-railway-app.railway.app/api/v1`

### Endpoints

#### 1. Generate Text Content

**POST** `/generate/text`

Generate rich HTML text content from topics and narrative.

**Request Body:**
```json
{
  "presentation_id": "pres_001",
  "slide_id": "slide_001",
  "slide_number": 1,
  "topics": [
    "Revenue growth",
    "Market expansion",
    "Cost efficiency"
  ],
  "narrative": "Strong Q3 performance across all metrics",
  "context": {
    "theme": "professional",
    "audience": "executives",
    "slide_title": "Q3 Financial Results"
  },
  "constraints": {
    "max_characters": 300,
    "style": "professional",
    "tone": "data-driven"
  }
}
```

**Response:**
```json
{
  "content": "<p>Q3 demonstrated <strong>exceptional revenue growth</strong>...</p>",
  "metadata": {
    "word_count": 48,
    "target_word_count": 54,
    "variance_percent": -11.1,
    "within_tolerance": false,
    "html_tags_used": ["p", "strong", "ul", "li", "span"],
    "generation_time_ms": 1245.3,
    "model_used": "gemini-2.0-flash-exp",
    "provider": "gemini",
    "prompt_tokens": 456,
    "completion_tokens": 182,
    "total_tokens": 638
  }
}
```

#### 2. Generate Table

**POST** `/generate/table`

Generate HTML table from data and description.

**Request Body:**
```json
{
  "presentation_id": "pres_001",
  "slide_id": "slide_002",
  "slide_number": 2,
  "description": "Regional revenue comparison Q2 vs Q3",
  "data": {
    "Q2": {"North America": 45.2, "Europe": 32.1, "Asia": 28.7},
    "Q3": {"North America": 58.3, "Europe": 39.4, "Asia": 35.6}
  },
  "context": {
    "theme": "professional",
    "audience": "executives",
    "slide_title": "Regional Performance"
  },
  "constraints": {
    "max_rows": 10,
    "max_columns": 5
  }
}
```

**Response:**
```json
{
  "html": "<table class=\"data-table\">...</table>",
  "metadata": {
    "rows": 3,
    "columns": 4,
    "data_points": 12,
    "has_header": true,
    "numeric_columns": 3,
    "generation_time_ms": 1876.2,
    "model_used": "gemini-2.0-flash-exp"
  }
}
```

#### 3. Batch Text Generation

**POST** `/generate/batch/text`

Generate text for multiple slides in one request.

```json
{
  "requests": [
    { /* TextGenerationRequest 1 */ },
    { /* TextGenerationRequest 2 */ }
  ],
  "parallel": true
}
```

#### 4. Get Session Info

**GET** `/session/{presentation_id}`

Retrieve session information.

**Response:**
```json
{
  "presentation_id": "pres_001",
  "slides_in_context": 3,
  "context_size_bytes": 2458,
  "last_updated": "2024-01-15T10:30:00",
  "ttl_remaining_seconds": 3240
}
```

#### 5. Delete Session

**DELETE** `/session/{presentation_id}`

Remove session and all context.

---

## 💡 Usage Examples

### Python Client Example

```python
import requests

API_URL = "http://localhost:8001/api/v1"

# Generate text content
text_request = {
    "presentation_id": "demo_pres",
    "slide_id": "slide_001",
    "slide_number": 1,
    "topics": ["Revenue growth", "Market expansion"],
    "narrative": "Strong quarterly performance",
    "context": {
        "theme": "professional",
        "audience": "executives",
        "slide_title": "Q3 Results"
    },
    "constraints": {
        "max_characters": 250
    }
}

response = requests.post(f"{API_URL}/generate/text", json=text_request)
result = response.json()

print("Generated Content:")
print(result["content"])
print(f"Word Count: {result['metadata']['word_count']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8001/api/v1/generate/text" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres_001",
    "slide_id": "slide_001",
    "slide_number": 1,
    "topics": ["Revenue growth"],
    "narrative": "Strong performance",
    "context": {
      "theme": "professional",
      "audience": "executives",
      "slide_title": "Q3 Results"
    },
    "constraints": {
      "max_characters": 200
    }
  }'
```

### JavaScript/TypeScript Example

```typescript
const API_URL = "http://localhost:8001/api/v1";

async function generateText(request: TextGenerationRequest) {
  const response = await fetch(`${API_URL}/generate/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  const result = await response.json();
  return result;
}

// Usage
const text = await generateText({
  presentation_id: "demo",
  slide_id: "slide_001",
  slide_number: 1,
  topics: ["Revenue growth"],
  narrative: "Strong Q3",
  context: {
    theme: "professional",
    audience: "executives",
    slide_title: "Q3 Results"
  },
  constraints: {
    max_characters: 300
  }
});
```

---

## 📝 System Prompts

System prompts are stored as markdown files in `app/prompts/` for easy editing:

### Editing Text Generation Prompt

Edit `app/prompts/text_generation.md` to customize:
- HTML formatting guidelines
- Word count optimization strategies
- Content flow instructions
- Quality standards

### Editing Table Generation Prompt

Edit `app/prompts/table_generation.md` to customize:
- Table structure guidelines
- Data presentation rules
- Formatting standards
- Column optimization logic

**Changes take effect immediately** - no restart required (prompts are loaded per request).

---

## 🚢 Deployment

### Railway Deployment

This service is pre-configured for Railway deployment.

#### Setup

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Initialize project
   railway init
   ```

2. **Configure Environment Variables**

   In Railway dashboard, add:
   ```
   GOOGLE_API_KEY=your_key_here
   LLM_PROVIDER=gemini
   LLM_MODEL=gemini-2.0-flash-exp
   ```

3. **Deploy**
   ```bash
   railway up
   ```

4. **Get URL**
   ```bash
   railway domain
   ```

#### Railway Configuration

The service includes:
- `railway.json` - Railway build and deploy config
- `Procfile` - Process definition
- `.gitignore` - Excludes sensitive files

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 🛠️ Development

### Project Structure

```
text_table_builder/v1.0/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── generators.py      # Text/Table generators
│   │   ├── llm_client.py      # LLM provider clients
│   │   └── session_manager.py # Session management
│   ├── models/
│   │   ├── requests.py        # Request models
│   │   ├── responses.py       # Response models
│   │   └── session.py         # Session models
│   ├── prompts/
│   │   ├── text_generation.md # Text prompt
│   │   └── table_generation.md# Table prompt
│   └── utils/
│       ├── html_utils.py      # HTML validation
│       └── prompt_loader.py   # Prompt loading
├── config/
├── tests/
├── main.py                    # FastAPI app
├── requirements.txt
├── .env.example
├── railway.json
├── Procfile
└── README.md
```

### Adding New Features

1. **Add New Endpoint**: Edit `app/api/routes.py`
2. **Modify Generation Logic**: Edit `app/core/generators.py`
3. **Update Prompts**: Edit markdown files in `app/prompts/`
4. **Add New Provider**: Extend `app/core/llm_client.py`

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

---

## 🧪 Testing

### Manual Testing

Use the interactive API docs at `/docs` to test endpoints.

### Automated Testing

```bash
# Run tests (when implemented)
pytest tests/

# With coverage
pytest --cov=app tests/
```

### Test Different Providers

```bash
# Test Gemini
LLM_PROVIDER=gemini python main.py

# Test OpenAI
LLM_PROVIDER=openai OPENAI_API_KEY=your_key python main.py

# Test Anthropic
LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=your_key python main.py
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **Import Errors**

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Ensure you're running from the project root:
```bash
cd text_table_builder/v1.0
python main.py
```

#### 2. **API Key Errors**

```
ValueError: GOOGLE_API_KEY not provided
```

**Solution**: Set API key in `.env` file:
```bash
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

#### 3. **Word Count Outside Tolerance**

```json
{
  "variance_percent": -15.0,
  "within_tolerance": false
}
```

**Solution**: Adjust tolerance in `.env`:
```bash
WORD_COUNT_TOLERANCE=0.20  # ±20%
```

#### 4. **Session Not Found**

```
404: Session not found
```

**Solution**: Sessions expire after TTL. Either:
- Increase `SESSION_CACHE_TTL`
- Use Redis for persistent sessions
- Generate content before session expires

### Logging

Enable debug logging:
```bash
LOG_LEVEL=debug python main.py
```

View JSON logs:
```bash
LOG_FORMAT=json python main.py
```

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` endpoint
- API Reference: See `/redoc` endpoint

---

## 🔮 Roadmap

- [ ] Streaming support for long content
- [ ] More LLM providers (Cohere, AI21)
- [ ] Content caching for performance
- [ ] Advanced HTML validation
- [ ] Custom CSS class configuration
- [ ] A/B testing for prompts
- [ ] Metrics and analytics dashboard

---

**Built with ❤️ using FastAPI, Pydantic, and Google Gemini**
