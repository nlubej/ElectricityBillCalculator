# Copilot Instructions - Electric Bill Calculator

## Project Overview
A Python application that connects to an API with X-API-KEY authentication to retrieve electric data.

## Key Implementation Details
- API key is stored securely in `.env` file (git-ignored)
- Uses `python-dotenv` to load environment variables
- All API requests include `X-API-KEY` header for authentication
- Error handling for missing configuration and API failures

## Development Rules
- Never hardcode API keys
- Always use environment variables for sensitive data
- Keep API client logic in `src/api_client.py`
- Main application logic in `src/main.py`
- Test with virtual environment before deploying
