"""Data processor for electric meter readings"""
from typing import Dict, Any, List


def calculate_consumption(interval_readings: List[Dict[str, Any]]) -> float:
    """
    Calculate consumption from interval readings.
    
    Args:
        interval_readings: List of reading objects with 'value' key
        
    Returns:
        Consumption as a float rounded to 4 decimals (last reading - first reading)
    """
    if not interval_readings or len(interval_readings) < 2:
        return 0.0
    
    first_value = float(interval_readings[0]['value'])
    last_value = float(interval_readings[-1]['value'])
    
    consumption = last_value - first_value
    return round(consumption, 4)


def process_meter_readings(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process raw meter readings data.
    
    Args:
        raw_data: Raw API response with intervalBlocks
        
    Returns:
        Processed data with consumption values for each reading type
    """
    processed_data = {
        'readings': []
    }
    
    if 'intervalBlocks' not in raw_data:
        return processed_data
    
    for block in raw_data['intervalBlocks']:
        reading_type = block.get('readingType', 'unknown')
        interval_readings = block.get('intervalReadings', [])
        
        consumption = calculate_consumption(interval_readings)
        
        processed_data['readings'].append({
            'readingType': reading_type,
            'consumption': consumption,
            'firstReading': float(interval_readings[0]['value']) if interval_readings else None,
            'lastReading': float(interval_readings[-1]['value']) if interval_readings else None,
            'readingCount': len(interval_readings)
        })
    
    return processed_data
