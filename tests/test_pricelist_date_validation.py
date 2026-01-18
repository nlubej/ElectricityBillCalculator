"""Tests for pricelist date validation"""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bill_calculator import ElectricityBillCalculator
from constants import READING_TYPE_VT, READING_TYPE_MT


class TestPricelistDateValidation:
    """Test pricelist date validation functionality"""
    
    def test_is_pricelist_valid_for_date_within_range(self):
        """Test that date within valid range returns True"""
        pricelist_data = {
            "validFrom": "2025-01-01",
            "validTo": "2025-12-31",
            "VT": 0.10,
            "MT": 0.15,
            "blocks": {
                "1": {"price": 0.15, "agreedPowerPrice": 0.05},
                "2": {"price": 0.20, "agreedPowerPrice": 0.06},
                "3": {"price": 0.25, "agreedPowerPrice": 0.07},
                "4": {"price": 0.30, "agreedPowerPrice": 0.08},
                "5": {"price": 0.35, "agreedPowerPrice": 0.09}
            },
            "additionalCosts": {
                "contributions": 0.37,
                "exciseDuty": 0.62,
                "monthlyAllowanceCost": 1.99,
                "discount": -0.18
            }
        }
        
        calculator = ElectricityBillCalculator(pricelist_data=pricelist_data)
        
        # Test dates within range
        assert calculator.is_pricelist_valid_for_date("2025-01-01") == True
        assert calculator.is_pricelist_valid_for_date("2025-06-15") == True
        assert calculator.is_pricelist_valid_for_date("2025-12-31") == True
    
    def test_is_pricelist_valid_for_date_outside_range(self):
        """Test that date outside valid range returns False"""
        pricelist_data = {
            "validFrom": "2025-01-01",
            "validTo": "2025-12-31",
            "VT": 0.10,
            "MT": 0.15,
            "blocks": {
                "1": {"price": 0.15, "agreedPowerPrice": 0.05},
                "2": {"price": 0.20, "agreedPowerPrice": 0.06},
                "3": {"price": 0.25, "agreedPowerPrice": 0.07},
                "4": {"price": 0.30, "agreedPowerPrice": 0.08},
                "5": {"price": 0.35, "agreedPowerPrice": 0.09}
            },
            "additionalCosts": {
                "contributions": 0.37,
                "exciseDuty": 0.62,
                "monthlyAllowanceCost": 1.99,
                "discount": -0.18
            }
        }
        
        calculator = ElectricityBillCalculator(pricelist_data=pricelist_data)
        
        # Test dates outside range
        assert calculator.is_pricelist_valid_for_date("2024-12-31") == False
        assert calculator.is_pricelist_valid_for_date("2026-01-01") == False
    
    def test_is_pricelist_valid_for_date_no_validity_dates(self):
        """Test that missing validFrom/validTo returns True (backward compatibility)"""
        pricelist_data = {
            "VT": 0.10,
            "MT": 0.15,
            "blocks": {
                "1": {"price": 0.15, "agreedPowerPrice": 0.05},
                "2": {"price": 0.20, "agreedPowerPrice": 0.06},
                "3": {"price": 0.25, "agreedPowerPrice": 0.07},
                "4": {"price": 0.30, "agreedPowerPrice": 0.08},
                "5": {"price": 0.35, "agreedPowerPrice": 0.09}
            },
            "additionalCosts": {
                "contributions": 0.37,
                "exciseDuty": 0.62,
                "monthlyAllowanceCost": 1.99,
                "discount": -0.18
            }
        }
        
        calculator = ElectricityBillCalculator(pricelist_data=pricelist_data)
        
        # Should return True for any date when no validity dates
        assert calculator.is_pricelist_valid_for_date("2024-01-01") == True
        assert calculator.is_pricelist_valid_for_date("2025-01-01") == True
        assert calculator.is_pricelist_valid_for_date("2026-01-01") == True
    
    def test_calculate_bill_raises_error_for_invalid_date(self):
        """Test that calculate_bill raises ValueError for date outside valid range"""
        pricelist_data = {
            "validFrom": "2025-01-01",
            "validTo": "2025-12-31",
            "VT": 0.10,
            "MT": 0.15,
            "blocks": {
                "1": {"price": 0.15, "agreedPowerPrice": 0.05},
                "2": {"price": 0.20, "agreedPowerPrice": 0.06},
                "3": {"price": 0.25, "agreedPowerPrice": 0.07},
                "4": {"price": 0.30, "agreedPowerPrice": 0.08},
                "5": {"price": 0.35, "agreedPowerPrice": 0.09}
            },
            "additionalCosts": {
                "contributions": 0.37,
                "exciseDuty": 0.62,
                "monthlyAllowanceCost": 1.99,
                "discount": -0.18
            }
        }
        
        consumption_data = {
            "consumption": [
                {
                    "month": "2024-12-01",
                    "block1": 100,
                    "block2": 150,
                    "block3": 100,
                    "block4": 50,
                    "block5": 0
                }
            ]
        }
        
        agreed_power_data = {
            "agreements": [
                {
                    "startDate": "2024-01-01",
                    "endDate": "2026-12-31",
                    "block1": 5,
                    "block2": 5,
                    "block3": 5,
                    "block4": 5,
                    "block5": 5
                }
            ]
        }
        
        calculator = ElectricityBillCalculator(
            consumption_data=consumption_data,
            pricelist_data=pricelist_data,
            agreed_power_data=agreed_power_data
        )
        
        monthly_data = {
            'readings': [
                {
                    'readingType': READING_TYPE_VT,
                    'consumption': 150.0
                },
                {
                    'readingType': READING_TYPE_MT,
                    'consumption': 200.0
                }
            ]
        }
        
        # Should raise ValueError for date outside valid range
        with pytest.raises(ValueError, match="Pricelist is not valid for date 2024-12-01"):
            calculator.calculate_bill(monthly_data, '2024-12-01')
    
    def test_calculate_bill_succeeds_for_valid_date(self):
        """Test that calculate_bill succeeds for date within valid range"""
        pricelist_data = {
            "validFrom": "2025-01-01",
            "validTo": "2025-12-31",
            "VT": 0.10,
            "MT": 0.15,
            "blocks": {
                "1": {"price": 0.15, "agreedPowerPrice": 0.05},
                "2": {"price": 0.20, "agreedPowerPrice": 0.06},
                "3": {"price": 0.25, "agreedPowerPrice": 0.07},
                "4": {"price": 0.30, "agreedPowerPrice": 0.08},
                "5": {"price": 0.35, "agreedPowerPrice": 0.09}
            },
            "additionalCosts": {
                "contributions": 0.37,
                "exciseDuty": 0.62,
                "monthlyAllowanceCost": 1.99,
                "discount": -0.18
            }
        }
        
        consumption_data = {
            "consumption": [
                {
                    "month": "2025-01-01",
                    "block1": 100,
                    "block2": 150,
                    "block3": 100,
                    "block4": 50,
                    "block5": 0
                }
            ]
        }
        
        agreed_power_data = {
            "agreements": [
                {
                    "startDate": "2025-01-01",
                    "endDate": "2025-12-31",
                    "block1": 5,
                    "block2": 5,
                    "block3": 5,
                    "block4": 5,
                    "block5": 5
                }
            ]
        }
        
        calculator = ElectricityBillCalculator(
            consumption_data=consumption_data,
            pricelist_data=pricelist_data,
            agreed_power_data=agreed_power_data
        )
        
        monthly_data = {
            'readings': [
                {
                    'readingType': READING_TYPE_VT,
                    'consumption': 150.0
                },
                {
                    'readingType': READING_TYPE_MT,
                    'consumption': 200.0
                }
            ]
        }
        
        # Should not raise any error
        bill = calculator.calculate_bill(monthly_data, '2025-01-01')
        assert 'amount' in bill
        assert bill['amount'] > 0
