# Electric Bill Calculator

A Python application that connects to an API with X-API-KEY authentication to retrieve electric data.

## Features

- Secure API key management using environment variables
- API client with X-API-KEY header authentication
- Function to retrieve electric data from the API

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key and base URL:
```
API_KEY=your_actual_api_key_here
API_BASE_URL=https://api.example.com
```

**Important:** Never commit `.env` to version control. The `.gitignore` file already excludes it.

## Usage

Run the application:

```bash
python src/main.py
```

## API Client

The `ElectricDataAPIClient` class provides the following method:

- `get_electric_data(user_id: str)` - Retrieves electric data for a specific user

### Example Usage

```python
from src.api_client import ElectricDataAPIClient

client = ElectricDataAPIClient()
data = client.get_electric_data("user_123")
print(data)
```

## Security

- API keys are stored in the `.env` file (which is in `.gitignore`)
- Never hardcode API keys in your code
- Use `python-dotenv` to safely load environment variables
- The API client automatically includes the `X-API-KEY` header in all requests

## Project Structure

```
ElectricBilCalculator/
├── src/
│   ├── api_client.py      # API client implementation
│   └── main.py            # Main application entry point
├── .env.example           # Example environment file
├── .env                   # Actual environment file (git-ignored)
├── .gitignore             # Git ignore configuration
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Dependencies

- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management

## Error Handling

The application includes error handling for:
- Missing API configuration
- Failed API requests
- Invalid responses

## Development

To modify the API client or add new functions:
1. Edit files in the `src/` directory
2. Test changes with `python src/main.py`
3. Update `requirements.txt` if adding new dependencies
