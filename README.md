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

The application will:
1. Retrieve meter readings from the API for configured usage points
2. Process the readings to calculate consumption (VT and MT)
3. Calculate monthly electricity bills based on pricelist and agreed power
4. Display detailed billing information

## Components

### API Client

The `ElectricDataAPIClient` class retrieves electric data from the API:

```python
from src.api_client import ElectricDataAPIClient

client = ElectricDataAPIClient()
data = client.get_meter_readings(usage_point, reading_type, start_date, end_date)
```

### Data Processor

The `process_meter_readings` function processes raw API data:

```python
from src.data_processor import process_meter_readings

processed_data = process_meter_readings(raw_api_response)
# Returns: {'consumption': float, 'start_date': str, 'end_date': str, ...}
```

### Bill Calculator

The `ElectricityBillCalculator` class calculates bills from consumption data:

```python
from src.bill_calculator import ElectricityBillCalculator

calculator = ElectricityBillCalculator()
bill = calculator.calculate_bill(consumption_vt, consumption_mt, start_date, end_date)
# Returns detailed bill breakdown including energy costs, network fees, taxes, etc.
```

## Security

- API keys are stored in the `.env` file (which is in `.gitignore`)
- Never hardcode API keys in your code
- Use `python-dotenv` to safely load environment variables
- The API client automatically includes the `X-API-KEY` header in all requests

## Project Structure

```
ElectricityBillCalculator/
├── src/
│   ├── api_client.py           # API client implementation
│   ├── bill_calculator.py      # Bill calculation logic
│   ├── constants.py            # Application constants
│   ├── data_processor.py       # Data processing utilities
│   └── main.py                 # Main application entry point
├── tests/
│   ├── test_agreed_power.py    # Agreed power tests
│   ├── test_api_client.py      # API client tests
│   ├── test_bill_calculation.py # Bill calculation tests
│   ├── test_data_processor.py  # Data processor tests
│   ├── test_pricelist.py       # Pricelist tests
│   └── test_pricelist_date_validation.py # Pricelist date validation tests
├── data/
│   ├── agreed_power.json       # Agreed power data
│   ├── consumption.json        # Consumption data
│   └── pricelist.json          # Pricing information
├── .env.example                # Example environment file
├── .env                        # Actual environment file (git-ignored)
├── .gitignore                  # Git ignore configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
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
