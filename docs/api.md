# API Reference

Complete reference for the ResumeX REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Current version does not require authentication. This will be added in future releases.

## Endpoints

### Root Information

#### `GET /`

Get API information.

**Response**

```json
{
  "message": "Welcome to ResumeX API",
  "version": "0.1.0"
}
```

---

### Health Check

#### `GET /health`

Check API health status.

**Response**

```json
{
  "status": "healthy"
}
```

---

### Analyze CV

#### `POST /api/v1/analyze`

Analyze a CV/Resume PDF.

**Request**

- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (file, required): PDF file to analyze
  - `language` (string, optional): Report language (default: "English")

**Supported Languages**

- English
- German
- French
- Italian
- Russian
- Turkish
- Spanish

**Response**

```json
{
  "language": "English",
  "domain_scores": [
    {
      "domain": "Software Development",
      "score": 85,
      "justification": "..."
    }
  ],
  "competency_scores": [
    {
      "category": "Technical Skills",
      "score": 90,
      "strength": "Strong in modern web technologies...",
      "observation": "Consider adding cloud certifications..."
    }
  ],
  "strategic_insights": "...",
  "development_recommendations": [
    "Add more leadership experience",
    "Obtain AWS certification"
  ],
  "overall_summary": {
    "overall_score": 82,
    "key_strengths": [
      "Strong technical foundation",
      "Good communication skills"
    ],
    "areas_to_improve": [
      "Leadership experience",
      "Industry certifications"
    ],
    "talent_potential": "High - Strong potential for senior roles"
  }
}
```

**Error Responses**

**400 Bad Request**

```json
{
  "detail": "Invalid file format. Only PDF files are supported."
}
```

**422 Unprocessable Entity**

```json
{
  "detail": [
    {
      "loc": ["body", "language"],
      "msg": "unsupported language",
      "type": "value_error"
    }
  ]
}
```

---

### Items API

#### `GET /api/v1/items/`

Get all items.

**Query Parameters**

- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Number of records to return (default: 100)

**Response**

```json
[]
```

#### `POST /api/v1/items/`

Create a new item.

**Request Body**

```json
{
  "title": "Item title",
  "description": "Item description"
}
```

**Response**

```json
{
  "message": "Item creation not yet implemented"
}
```

#### `GET /api/v1/items/{item_id}`

Get a specific item.

**Path Parameters**

- `item_id` (integer, required): Item identifier

**Response**

**404 Not Found**

```json
{
  "detail": "Item not found"
}
```

#### `PUT /api/v1/items/{item_id}`

Update an item.

**Path Parameters**

- `item_id` (integer, required): Item identifier

**Response**

**404 Not Found**

```json
{
  "detail": "Item not found"
}
```

#### `DELETE /api/v1/items/{item_id}`

Delete an item.

**Path Parameters**

- `item_id` (integer, required): Item identifier

**Response**

**404 Not Found**

```json
{
  "detail": "Item not found"
}
```

---

## Error Responses

All endpoints may return these error responses:

### 500 Internal Server Error

```json
{
  "detail": "An internal error occurred"
}
```

### 503 Service Unavailable

```json
{
  "detail": "Service temporarily unavailable"
}
```

## Rate Limiting

Currently, no rate limiting is enforced. This will be added in future releases.

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Code Examples

### Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Analyze CV
with open("cv.pdf", "rb") as f:
    files = {"file": f}
    data = {"language": "English"}
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        files=files,
        data=data
    )
    print(response.json())
```

### JavaScript

```javascript
// Health check
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Analyze CV
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('language', 'English');

fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Analyze CV
curl -X POST \
  http://localhost:8000/api/v1/analyze \
  -F "file=@cv.pdf" \
  -F "language=English"
```

## Versioning

The API uses semantic versioning. Current version: **v0.1.0**

## Support

For API issues or questions:

- GitHub Issues: [HappyHackingSpace/resumex/issues](https://github.com/HappyHackingSpace/resumex/issues)
- Discord: [Happy Hacking Space](https://discord.gg/happyhackingspace)
