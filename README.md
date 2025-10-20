# Text and Table Content Builder v1.0

LLM-powered content generation microservice for presentation slides. Generates rich HTML text and tables with context retention and word count control.

## 🌐 Production Deployment

**Live API**: https://web-production-e3796.up.railway.app

**Status**: ✅ Operational
**Provider**: Railway
**Region**: US East

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

- [Production Deployment](#production-deployment)
- [External Service Integration](#external-service-integration)
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

## 🔌 External Service Integration

This section shows how to integrate the Text & Table Builder API into your external services (Content Orchestrator, presentation builders, etc.).

### 🌐 Production API Endpoint

```
Base URL: https://web-production-e3796.up.railway.app
```

### 🔑 Quick Integration Guide

#### 1. **Python Integration (Recommended for Content Orchestrator)**

```python
import requests
from typing import Dict, Any, List

class TextTableBuilderClient:
    """Client for Text & Table Builder API."""

    def __init__(self, base_url: str = "https://web-production-e3796.up.railway.app"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def generate_text(
        self,
        presentation_id: str,
        slide_id: str,
        slide_number: int,
        topics: List[str],
        narrative: str,
        context: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate HTML text content for a slide.

        Args:
            presentation_id: Unique presentation identifier
            slide_id: Slide identifier
            slide_number: Slide number in sequence
            topics: List of key points to cover
            narrative: Overall slide narrative
            context: Presentation context (theme, audience, slide_title)
            constraints: Generation constraints (max_characters)

        Returns:
            Dictionary with 'content' (HTML) and 'metadata'
        """
        endpoint = f"{self.api_base}/generate/text"

        payload = {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "slide_number": slide_number,
            "topics": topics,
            "narrative": narrative,
            "context": context,
            "constraints": constraints
        }

        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def generate_table(
        self,
        presentation_id: str,
        slide_id: str,
        slide_number: int,
        description: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate HTML table from data.

        Args:
            presentation_id: Unique presentation identifier
            slide_id: Slide identifier
            slide_number: Slide number in sequence
            description: What the table should show
            data: Raw data to structure into table
            context: Presentation context (theme, audience, slide_title)
            constraints: Table constraints (max_rows, max_columns)

        Returns:
            Dictionary with 'html' (table markup) and 'metadata'
        """
        endpoint = f"{self.api_base}/generate/table"

        payload = {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "slide_number": slide_number,
            "description": description,
            "data": data,
            "context": context,
            "constraints": constraints or {}
        }

        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_session_info(self, presentation_id: str) -> Dict[str, Any]:
        """Get session information for a presentation."""
        endpoint = f"{self.api_base}/session/{presentation_id}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()

    def delete_session(self, presentation_id: str) -> Dict[str, Any]:
        """Delete a presentation session."""
        endpoint = f"{self.api_base}/session/{presentation_id}"
        response = requests.delete(endpoint)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        endpoint = f"{self.base_url}/health"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()


# Usage Example
if __name__ == "__main__":
    client = TextTableBuilderClient()

    # Check API health
    health = client.health_check()
    print(f"API Status: {health['status']}")

    # Generate text content
    text_result = client.generate_text(
        presentation_id="pres_001",
        slide_id="slide_001",
        slide_number=1,
        topics=["Revenue growth", "Market expansion"],
        narrative="Strong Q3 performance",
        context={
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Q3 Results"
        },
        constraints={
            "max_characters": 250
        }
    )

    print(f"Generated HTML: {text_result['content']}")
    print(f"Word Count: {text_result['metadata']['word_count']}")
```

#### 2. **JavaScript/TypeScript Integration**

```typescript
interface TextGenerationRequest {
  presentation_id: string;
  slide_id: string;
  slide_number: number;
  topics: string[];
  narrative: string;
  context: {
    theme: string;
    audience: string;
    slide_title: string;
  };
  constraints: {
    max_characters: number;
  };
}

interface GeneratedText {
  content: string;
  metadata: {
    word_count: number;
    target_word_count: number;
    html_tags_used: string[];
    generation_time_ms: number;
    model_used: string;
  };
}

class TextTableBuilderClient {
  private baseUrl: string;
  private apiBase: string;

  constructor(baseUrl: string = "https://web-production-e3796.up.railway.app") {
    this.baseUrl = baseUrl;
    this.apiBase = `${baseUrl}/api/v1`;
  }

  async generateText(request: TextGenerationRequest): Promise<GeneratedText> {
    const response = await fetch(`${this.apiBase}/generate/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  }

  async generateTable(request: any): Promise<any> {
    const response = await fetch(`${this.apiBase}/generate/table`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  }

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}

// Usage
const client = new TextTableBuilderClient();

const result = await client.generateText({
  presentation_id: "pres_001",
  slide_id: "slide_001",
  slide_number: 1,
  topics: ["Revenue growth", "Market expansion"],
  narrative: "Strong Q3 performance",
  context: {
    theme: "professional",
    audience: "executives",
    slide_title: "Q3 Results"
  },
  constraints: {
    max_characters: 250
  }
});

console.log("Generated HTML:", result.content);
```

#### 3. **cURL Examples (for Testing)**

**Generate Text**:
```bash
curl -X POST "https://web-production-e3796.up.railway.app/api/v1/generate/text" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres_001",
    "slide_id": "slide_001",
    "slide_number": 1,
    "topics": ["Revenue growth", "Market expansion"],
    "narrative": "Strong Q3 performance",
    "context": {
      "theme": "professional",
      "audience": "executives",
      "slide_title": "Q3 Results"
    },
    "constraints": {
      "max_characters": 250
    }
  }'
```

**Generate Table**:
```bash
curl -X POST "https://web-production-e3796.up.railway.app/api/v1/generate/table" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres_001",
    "slide_id": "slide_002",
    "slide_number": 2,
    "description": "Regional revenue comparison Q2 vs Q3",
    "data": {
      "Q2": {"North America": 45.2, "Europe": 32.1},
      "Q3": {"North America": 58.3, "Europe": 39.4}
    },
    "context": {
      "theme": "professional",
      "audience": "executives",
      "slide_title": "Regional Performance"
    }
  }'
```

**Check Health**:
```bash
curl https://web-production-e3796.up.railway.app/health
```

#### 4. **REST API Client (Generic)**

For any HTTP client library:

**Base Configuration**:
- **Base URL**: `https://web-production-e3796.up.railway.app`
- **Content-Type**: `application/json`
- **Timeout**: 30 seconds (LLM generation can take 5-15 seconds)
- **Retry Policy**: Recommended with exponential backoff

**Endpoints**:
- `POST /api/v1/generate/text` - Generate HTML text
- `POST /api/v1/generate/table` - Generate HTML table
- `POST /api/v1/generate/batch/text` - Batch text generation
- `POST /api/v1/generate/batch/table` - Batch table generation
- `GET /api/v1/session/{presentation_id}` - Get session info
- `DELETE /api/v1/session/{presentation_id}` - Delete session
- `GET /health` - Health check
- `GET /api/v1/health` - API health check

### 📊 Response Format

#### Text Generation Response
```json
{
  "content": "<p>Generated HTML content...</p>",
  "metadata": {
    "word_count": 42,
    "target_word_count": 50,
    "variance_percent": -16.0,
    "within_tolerance": false,
    "html_tags_used": ["p", "strong", "ul", "li"],
    "generation_time_ms": 8500.0,
    "model_used": "gemini-2.5-flash",
    "provider": "gemini",
    "prompt_tokens": 1200,
    "completion_tokens": 150,
    "total_tokens": 1350
  }
}
```

#### Table Generation Response
```json
{
  "html": "<table class=\"data-table\">...</table>",
  "metadata": {
    "rows": 4,
    "columns": 4,
    "data_points": 16,
    "has_header": true,
    "numeric_columns": 3,
    "generation_time_ms": 9200.0,
    "model_used": "gemini-2.5-flash",
    "provider": "gemini",
    "table_classes": ["data-table", "numeric", "metric"]
  }
}
```

### 🔄 Session Management

The API automatically manages sessions per `presentation_id`:

1. **Automatic Session Creation**: First request with a `presentation_id` creates a session
2. **Context Retention**: Maintains history of last 5 slides for content flow
3. **Session TTL**: Sessions expire after 1 hour of inactivity
4. **Session Info**: Query session status with `GET /api/v1/session/{presentation_id}`
5. **Cleanup**: Delete sessions when presentation is complete

**Best Practices**:
- Use consistent `presentation_id` across all slides in a presentation
- Delete sessions after presentation generation completes
- Sessions auto-expire after 1 hour (configurable)

### ⚡ Performance Considerations

- **Average Response Time**: 5-15 seconds (LLM generation)
- **Concurrent Requests**: Supports up to 10 concurrent requests
- **Rate Limiting**: No rate limiting currently (use responsibly)
- **Timeout**: Set client timeout to 30 seconds minimum
- **Caching**: Context cached per session (1 hour TTL)

### 🛡️ Error Handling

**Common HTTP Status Codes**:
- `200 OK` - Successful generation
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Session or endpoint not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error (retry recommended)
- `503 Service Unavailable` - Service temporarily unavailable

**Example Error Response**:
```json
{
  "detail": "Error message describing the issue"
}
```

**Recommended Error Handling**:
```python
try:
    result = client.generate_text(...)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        print(f"Validation error: {e.response.json()}")
    elif e.response.status_code >= 500:
        print("Server error, retrying...")
        # Implement retry logic
    else:
        print(f"Error: {e}")
except requests.exceptions.Timeout:
    print("Request timed out, LLM generation may take longer")
```

### 📚 Interactive API Documentation

**Swagger UI**: https://web-production-e3796.up.railway.app/docs

Features:
- Try out all endpoints directly in browser
- See request/response schemas
- View example payloads
- Test authentication and headers

### 🔗 Integration with Content Orchestrator

**Example Integration in Content Orchestrator**:

```python
# In Content Orchestrator configuration
TEXT_TABLE_BUILDER_URL = "https://web-production-e3796.up.railway.app"
TEXT_TABLE_BUILDER_TIMEOUT = 30

# In your content generation logic
from clients.text_table_client import TextTableBuilderClient

class ContentOrchestrator:
    def __init__(self):
        self.text_table_client = TextTableBuilderClient(
            base_url=TEXT_TABLE_BUILDER_URL
        )

    def enrich_slide_with_text(self, slide_data: dict) -> dict:
        """Enrich slide with generated text content."""
        result = self.text_table_client.generate_text(
            presentation_id=slide_data["presentation_id"],
            slide_id=slide_data["slide_id"],
            slide_number=slide_data["slide_number"],
            topics=slide_data["key_points"],
            narrative=slide_data["narrative"],
            context={
                "theme": slide_data["theme"],
                "audience": slide_data["audience"],
                "slide_title": slide_data["title"]
            },
            constraints={
                "max_characters": slide_data.get("max_characters", 300)
            }
        )

        slide_data["enriched_content"] = result["content"]
        slide_data["content_metadata"] = result["metadata"]
        return slide_data
```

### 🚀 Quick Start Integration

**Minimal Integration** (5 minutes):

```python
import requests

API_URL = "https://web-production-e3796.up.railway.app/api/v1"

# Generate text for a slide
response = requests.post(
    f"{API_URL}/generate/text",
    json={
        "presentation_id": "my_pres",
        "slide_id": "slide_1",
        "slide_number": 1,
        "topics": ["Topic 1", "Topic 2"],
        "narrative": "Brief narrative",
        "context": {"theme": "professional", "audience": "general", "slide_title": "Title"},
        "constraints": {"max_characters": 200}
    },
    timeout=30
)

html_content = response.json()["content"]
print(html_content)
```

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
LLM_MAX_TOKENS=60000

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
