"""Test cases for Electric Data API Client"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api_client import ElectricDataAPIClient
from constants import READING_TYPE_VT, READING_TYPE_MT


@pytest.fixture
def mock_api_client(monkeypatch):
    """Create a mock API client for testing"""
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return MOCK_API_RESPONSE_BOTH_TYPES
            def raise_for_status(self):
                pass
        return MockResponse()
    
    monkeypatch.setenv('API_KEY', 'test_api_key')
    monkeypatch.setenv('API_BASE_URL', 'https://api.example.com')
    monkeypatch.setattr('requests.get', mock_get)
    
    return ElectricDataAPIClient()


MOCK_API_RESPONSE_BOTH_TYPES = {
    "intervalBlocks": [
        {
            "readingType": READING_TYPE_VT,
            "intervalReadings": [
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-01T00:00:00+01:00",
                    "value": "18558.0840"
                },
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-02T00:00:00+01:00",
                    "value": "18596.8720"
                },
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-03T00:00:00+01:00",
                    "value": "18623.4440"
                }
            ]
        },
        {
            "readingType": READING_TYPE_MT,
            "intervalReadings": [
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-01T00:00:00+01:00",
                    "value": "1200.5420"
                },
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-02T00:00:00+01:00",
                    "value": "1245.3310"
                },
                {
                    "readingQualities": [],
                    "timestamp": "2025-01-03T00:00:00+01:00",
                    "value": "1290.7650"
                }
            ]
        }
    ]
}


class TestReadingTypes:
    """Test reading type constants"""
    
    def test_reading_type_vt_constant(self):
        """Test VT reading type constant"""
        assert READING_TYPE_VT == "32.0.4.1.1.2.12.0.0.0.0.1.0.0.0.3.72.0"
    
    def test_reading_type_mt_constant(self):
        """Test MT reading type constant"""
        assert READING_TYPE_MT == "32.0.4.1.1.2.12.0.0.0.0.2.0.0.0.3.72.0"


class TestAPIClient:
    """Test API client functionality"""
    
    def test_client_initialization(self, monkeypatch):
        """Test API client initialization"""
        monkeypatch.setenv('API_KEY', 'test_key')
        monkeypatch.setenv('API_BASE_URL', 'https://api.example.com')
        
        client = ElectricDataAPIClient()
        assert client.api_key == 'test_key'
        assert client.base_url == 'https://api.example.com'
    
    def test_client_missing_api_key(self, monkeypatch):
        """Test that client raises error when API key is missing"""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.setenv('API_BASE_URL', 'https://api.example.com')
        
        with pytest.raises(ValueError, match="API_KEY not provided"):
            ElectricDataAPIClient()
    
    def test_client_missing_base_url(self, monkeypatch):
        """Test that client raises error when base URL is missing"""
        monkeypatch.setenv('API_KEY', 'test_key')
        monkeypatch.delenv('API_BASE_URL', raising=False)
        
        with pytest.raises(ValueError, match="API_BASE_URL not provided"):
            ElectricDataAPIClient()
    
    def test_get_headers(self, mock_api_client):
        """Test that headers include X-API-TOKEN"""
        headers = mock_api_client._get_headers()
        assert 'X-API-TOKEN' in headers
        assert headers['X-API-TOKEN'] == 'test_api_key'
        assert headers['Content-Type'] == 'application/json'
    
    def test_get_electric_data(self, mock_api_client):
        """Test retrieving electric data"""
        result = mock_api_client.get_electric_data('3-256908', '2025-01-01', '2025-02-01', [READING_TYPE_VT, READING_TYPE_MT])
        
        assert 'intervalBlocks' in result
        assert len(result['intervalBlocks']) > 0
        assert 'intervalReadings' in result['intervalBlocks'][0]
    
    def test_interval_readings_structure(self, mock_api_client):
        """Test that interval readings have expected structure"""
        result = mock_api_client.get_electric_data('3-256908', '2025-01-01', '2025-02-01', [READING_TYPE_VT, READING_TYPE_MT])
        
        # Should have both VT and MT reading types
        assert len(result['intervalBlocks']) == 2
        
        # Check VT block
        vt_block = result['intervalBlocks'][0]
        assert vt_block['readingType'] == READING_TYPE_VT
        vt_readings = vt_block['intervalReadings']
        assert len(vt_readings) == 3
        assert vt_readings[0]['value'] == '18558.0840'
        
        # Check MT block
        mt_block = result['intervalBlocks'][1]
        assert mt_block['readingType'] == READING_TYPE_MT
        mt_readings = mt_block['intervalReadings']
        assert len(mt_readings) == 3
        assert mt_readings[0]['value'] == '1200.5420'
    
    def test_vt_reading_type_values(self, mock_api_client):
        """Test VT reading type specific values"""
        result = mock_api_client.get_electric_data('3-256908', '2025-01-01', '2025-02-01', [READING_TYPE_VT, READING_TYPE_MT])
        vt_block = result['intervalBlocks'][0]
        
        assert vt_block['readingType'] == READING_TYPE_VT
        readings = vt_block['intervalReadings']
        
        expected_values = ['18558.0840', '18596.8720', '18623.4440']
        actual_values = [r['value'] for r in readings]
        
        assert actual_values == expected_values
    
    def test_mt_reading_type_values(self, mock_api_client):
        """Test MT reading type specific values"""
        result = mock_api_client.get_electric_data('3-256908', '2025-01-01', '2025-02-01', [READING_TYPE_VT, READING_TYPE_MT])
        mt_block = result['intervalBlocks'][1]
        
        assert mt_block['readingType'] == READING_TYPE_MT
        readings = mt_block['intervalReadings']
        
        expected_values = ['1200.5420', '1245.3310', '1290.7650']
        actual_values = [r['value'] for r in readings]
        
        assert actual_values == expected_values
    
    def test_reading_values_type(self, mock_api_client):
        """Test that reading values are strings"""
        result = mock_api_client.get_electric_data('3-256908', '2025-01-01', '2025-02-01', [READING_TYPE_VT, READING_TYPE_MT])
        readings = result['intervalBlocks'][0]['intervalReadings']
        
        for reading in readings:
            assert isinstance(reading['value'], str)
            assert isinstance(reading['timestamp'], str)
