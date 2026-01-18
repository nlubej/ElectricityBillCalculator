"""Tests for pricelist structure and data validation"""
import os
import json
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestPricelistStructure:
    """Test pricelist.json has all required properties"""
    
    @pytest.fixture
    def pricelist_path(self):
        """Get the path to pricelist.json"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', 'data', 'pricelist.json')
    
    @pytest.fixture
    def pricelist_data(self, pricelist_path):
        """Load pricelist data"""
        with open(pricelist_path, 'r') as f:
            return json.load(f)
    
    def test_pricelist_file_exists(self, pricelist_path):
        """Test that pricelist.json file exists"""
        assert os.path.exists(pricelist_path), "pricelist.json file should exist"
    
    def test_pricelist_has_vt_tariff(self, pricelist_data):
        """Test that pricelist has VT (Low Tariff) property"""
        assert 'VT' in pricelist_data, "pricelist should have 'VT' property"
        assert isinstance(pricelist_data['VT'], (int, float)), "VT should be a number"
        assert pricelist_data['VT'] >= 0, "VT should be non-negative"
    
    def test_pricelist_has_mt_tariff(self, pricelist_data):
        """Test that pricelist has MT (High Tariff) property"""
        assert 'MT' in pricelist_data, "pricelist should have 'MT' property"
        assert isinstance(pricelist_data['MT'], (int, float)), "MT should be a number"
        assert pricelist_data['MT'] >= 0, "MT should be non-negative"
    
    def test_pricelist_has_blocks(self, pricelist_data):
        """Test that pricelist has blocks property"""
        assert 'blocks' in pricelist_data, "pricelist should have 'blocks' property"
        assert isinstance(pricelist_data['blocks'], dict), "blocks should be a dictionary"
    
    def test_pricelist_has_all_five_blocks(self, pricelist_data):
        """Test that pricelist has all 5 blocks (1-5)"""
        blocks = pricelist_data['blocks']
        for block_num in range(1, 6):
            block_key = str(block_num)
            assert block_key in blocks, f"Block {block_num} should exist in pricelist"
    
    def test_each_block_has_price(self, pricelist_data):
        """Test that each block has a 'price' property"""
        blocks = pricelist_data['blocks']
        for block_num in range(1, 6):
            block_key = str(block_num)
            block_data = blocks[block_key]
            assert 'price' in block_data, f"Block {block_num} should have 'price' property"
            assert isinstance(block_data['price'], (int, float)), f"Block {block_num} price should be a number"
            assert block_data['price'] >= 0, f"Block {block_num} price should be non-negative"
    
    def test_each_block_has_agreed_power_price(self, pricelist_data):
        """Test that each block has an 'agreedPowerPrice' property"""
        blocks = pricelist_data['blocks']
        for block_num in range(1, 6):
            block_key = str(block_num)
            block_data = blocks[block_key]
            assert 'agreedPowerPrice' in block_data, f"Block {block_num} should have 'agreedPowerPrice' property"
            assert isinstance(block_data['agreedPowerPrice'], (int, float)), f"Block {block_num} agreedPowerPrice should be a number"
            assert block_data['agreedPowerPrice'] >= 0, f"Block {block_num} agreedPowerPrice should be non-negative"
    
    def test_block_properties_complete(self, pricelist_data):
        """Test that each block has exactly 'price' and 'agreedPowerPrice' properties"""
        blocks = pricelist_data['blocks']
        required_properties = {'price', 'agreedPowerPrice'}
        
        for block_num in range(1, 6):
            block_key = str(block_num)
            block_data = blocks[block_key]
            block_properties = set(block_data.keys())
            assert block_properties == required_properties, \
                f"Block {block_num} should have exactly 'price' and 'agreedPowerPrice' properties"
    
    def test_pricelist_top_level_properties(self, pricelist_data):
        """Test that pricelist has required top level properties"""
        required_properties = {'VT', 'MT', 'blocks', 'additionalCosts', 'validFrom', 'validTo'}
        actual_properties = set(pricelist_data.keys())
        assert actual_properties == required_properties, \
            f"pricelist should have 'VT', 'MT', 'blocks', 'additionalCosts', 'validFrom', and 'validTo' properties. Found: {actual_properties}"
    
    def test_pricelist_has_valid_dates(self, pricelist_data):
        """Test that pricelist has validFrom and validTo date properties"""
        assert 'validFrom' in pricelist_data, "pricelist should have 'validFrom' property"
        assert 'validTo' in pricelist_data, "pricelist should have 'validTo' property"
        
        # Verify date format (YYYY-MM-DD)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        assert re.match(date_pattern, pricelist_data['validFrom']), "validFrom should be in YYYY-MM-DD format"
        assert re.match(date_pattern, pricelist_data['validTo']), "validTo should be in YYYY-MM-DD format"
        
        # Verify validFrom is before or equal to validTo
        assert pricelist_data['validFrom'] <= pricelist_data['validTo'], "validFrom should be before or equal to validTo"
    
    def test_pricelist_has_additional_costs(self, pricelist_data):
        """Test that pricelist has additionalCosts with required properties"""
        assert 'additionalCosts' in pricelist_data, "pricelist should have 'additionalCosts' property"
        additional_costs = pricelist_data['additionalCosts']
        
        required_cost_properties = {'contributions', 'exciseDuty', 'monthlyAllowanceCost', 'discount'}
        actual_cost_properties = set(additional_costs.keys())
        assert actual_cost_properties == required_cost_properties, \
            f"additionalCosts should have {required_cost_properties}. Found: {actual_cost_properties}"
        
        # Verify all are numbers
        for key, value in additional_costs.items():
            assert isinstance(value, (int, float)), f"additionalCosts.{key} should be a number"
