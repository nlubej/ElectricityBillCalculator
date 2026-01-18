"""Test cases for Data Processor"""
import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from constants import READING_TYPE_VT, READING_TYPE_MT
from data_processor import calculate_consumption, process_meter_readings


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


class TestDataProcessor:
    """Test data processor functions"""
    
    def test_calculate_consumption_basic(self):
        """Test basic consumption calculation"""
        readings = [
            {'value': '100.0000'},
            {'value': '150.0000'}
        ]
        consumption = calculate_consumption(readings)
        assert consumption == 50.0
    
    def test_calculate_consumption_rounded(self):
        """Test consumption is rounded to 4 decimals"""
        readings = [
            {'value': '100.123456'},
            {'value': '150.789012'}
        ]
        consumption = calculate_consumption(readings)
        assert consumption == 50.6656  # Rounded to 4 decimals
    
    def test_calculate_consumption_empty(self):
        """Test consumption with empty readings"""
        consumption = calculate_consumption([])
        assert consumption == 0.0
    
    def test_process_meter_readings_both_types(self):
        """Test processing both VT and MT meter readings"""
        processed = process_meter_readings(MOCK_API_RESPONSE_BOTH_TYPES)
        
        assert 'readings' in processed
        assert len(processed['readings']) == 2
        
        # Check VT
        vt_reading = processed['readings'][0]
        assert vt_reading['readingType'] == READING_TYPE_VT
        assert vt_reading['consumption'] == 65.3600
        vt_consumption = vt_reading['consumption']
        
        # Check MT
        mt_reading = processed['readings'][1]
        assert mt_reading['readingType'] == READING_TYPE_MT
        assert mt_reading['consumption'] == 90.2230
        mt_consumption = mt_reading['consumption']
        
        # Check ET (sum of MT and VT)
        et_total = vt_consumption + mt_consumption
        assert et_total == 155.5830
    
    def test_process_meter_readings_empty(self):
        """Test processing empty meter readings"""
        processed = process_meter_readings({})
        
        assert 'readings' in processed
        assert len(processed['readings']) == 0
