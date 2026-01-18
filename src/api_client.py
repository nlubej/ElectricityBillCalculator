"""API Client for Electric Data"""
import os
import requests
from typing import Dict, Any, Optional
from constants import READING_TYPE_VT, READING_TYPE_MT


class ElectricDataAPIClient:
    """Client for retrieving electricity data from API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: API key (defaults to API_KEY environment variable)
            base_url: Base URL for the API (defaults to API_BASE_URL environment variable)
        """
        self.api_key = api_key or os.getenv('API_KEY')
        self.base_url = base_url or os.getenv('API_BASE_URL')
        
        if not self.api_key:
            raise ValueError("API_KEY not provided and not found in environment variables")
        if not self.base_url:
            raise ValueError("API_BASE_URL not provided and not found in environment variables")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API token"""
        return {
            'X-API-TOKEN': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_electric_data(self, usage_point: str, start_time: str, end_time: str, reading_types: list) -> Dict[str, Any]:
        """
        Retrieve electric data for a usage point.
        
        Args:
            usage_point: The usage point to retrieve data for
            start_time: Start time for data retrieval (format: YYYY-MM-DD)
            end_time: End time for data retrieval (format: YYYY-MM-DD)
            reading_types: List of reading types to retrieve
            
        Returns:
            Dictionary containing electric data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        params = {'usagePoint': usage_point}
        params['startTime'] = start_time
        params['endTime'] = end_time
        
        # Add reading type options
        options = [f'ReadingType={rt}' for rt in reading_types]
        params['option'] = options
        
        url = f"{self.base_url}/meter-readings"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve electric data: {str(e)}")
