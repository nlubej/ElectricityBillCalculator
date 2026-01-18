"""Tests for agreed power structure and data validation"""
import os
import json
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestAgreedPowerStructure:
    """Test agreed_power.json has all required properties"""
    
    @pytest.fixture
    def agreed_power_path(self):
        """Get the path to agreed_power.json"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', 'data', 'agreed_power.json')
    
    @pytest.fixture
    def agreed_power_data(self, agreed_power_path):
        """Load agreed power data"""
        with open(agreed_power_path, 'r') as f:
            return json.load(f)
    
    def test_agreed_power_file_exists(self, agreed_power_path):
        """Test that agreed_power.json file exists"""
        assert os.path.exists(agreed_power_path), "agreed_power.json file should exist"
    
    def test_agreed_power_has_agreements(self, agreed_power_data):
        """Test that agreed_power has 'agreements' array"""
        assert 'agreements' in agreed_power_data, "agreed_power should have 'agreements' property"
        assert isinstance(agreed_power_data['agreements'], list), "agreements should be a list"
        assert len(agreed_power_data['agreements']) > 0, "agreements should not be empty"
    
    def test_each_agreement_has_dates(self, agreed_power_data):
        """Test that each agreement has startDate and endDate"""
        for idx, agreement in enumerate(agreed_power_data['agreements']):
            assert 'startDate' in agreement, f"Agreement {idx} should have 'startDate'"
            assert 'endDate' in agreement, f"Agreement {idx} should have 'endDate'"
            
            # Validate date format
            try:
                datetime.strptime(agreement['startDate'], '%Y-%m-%d')
                datetime.strptime(agreement['endDate'], '%Y-%m-%d')
            except ValueError:
                pytest.fail(f"Agreement {idx} dates should be in YYYY-MM-DD format")
    
    def test_each_agreement_has_all_blocks(self, agreed_power_data):
        """Test that each agreement has all 5 blocks"""
        for idx, agreement in enumerate(agreed_power_data['agreements']):
            for block_num in range(1, 6):
                block_key = f'block{block_num}'
                assert block_key in agreement, f"Agreement {idx} should have '{block_key}'"
                assert isinstance(agreement[block_key], (int, float)), \
                    f"Agreement {idx} {block_key} should be a number"
                assert agreement[block_key] >= 0, \
                    f"Agreement {idx} {block_key} should be non-negative"
    
    def test_agreement_properties_complete(self, agreed_power_data):
        """Test that each agreement has exactly required properties"""
        required_properties = {'startDate', 'endDate', 'block1', 'block2', 'block3', 'block4', 'block5'}
        
        for idx, agreement in enumerate(agreed_power_data['agreements']):
            agreement_properties = set(agreement.keys())
            assert agreement_properties == required_properties, \
                f"Agreement {idx} should have exactly: {required_properties}. Found: {agreement_properties}"
    
    def test_date_ranges_not_overlapping(self, agreed_power_data):
        """Test that agreement date ranges do not overlap"""
        agreements = agreed_power_data['agreements']
        
        for i in range(len(agreements)):
            start_i = datetime.strptime(agreements[i]['startDate'], '%Y-%m-%d')
            end_i = datetime.strptime(agreements[i]['endDate'], '%Y-%m-%d')
            
            assert start_i <= end_i, f"Agreement {i} startDate should be <= endDate"
            
            for j in range(i + 1, len(agreements)):
                start_j = datetime.strptime(agreements[j]['startDate'], '%Y-%m-%d')
                end_j = datetime.strptime(agreements[j]['endDate'], '%Y-%m-%d')
                
                # Check no overlap
                overlap = not (end_i < start_j or end_j < start_i)
                assert not overlap, f"Agreements {i} and {j} should not overlap"
    
    def test_top_level_properties(self, agreed_power_data):
        """Test that agreed_power has exactly 'agreements' at top level"""
        required_properties = {'agreements'}
        actual_properties = set(agreed_power_data.keys())
        assert actual_properties == required_properties, \
            f"agreed_power should have exactly 'agreements' property. Found: {actual_properties}"
