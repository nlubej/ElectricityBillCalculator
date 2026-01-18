"""Test bill calculation logic"""
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bill_calculator import ElectricityBillCalculator
from constants import READING_TYPE_VT, READING_TYPE_MT


def test_bill_calculation_sister():
    """Test bill calculation with injected data (no file IO)."""
    # Inject custom pricelist, agreed power, and consumption data
    injected_pricelist = {
        "VT": 0.084,
        "MT": 0.07,
        "blocks": {
            "1": {"price": 0.019580, "agreedPowerPrice": 3.61324},
            "2": {"price": 0.018440, "agreedPowerPrice": 0.8824},
            "3": {"price": 0.018370, "agreedPowerPrice": 0.191370},
            "4": {"price": 0.018380, "agreedPowerPrice": 0.013160},
            "5": {"price": 0, "agreedPowerPrice": 0}
        },
        "additionalCosts": {
            "contributions": 0.37,
            "exciseDuty": 0.62,
            "monthlyAllowanceCost": 1.99,
            "discount": -0.18
        }
    }

    injected_agreed_power = {
        "agreements": [
            {
                "startDate": "2025-01-01",
                "endDate": "2025-12-31",
                "block1": 5,
                "block2": 5.3,
                "block3": 5.6,
                "block4": 5.6,
                "block5": 5.6
            }
        ]
    }

    injected_consumption = {
        "consumption": [
            {
                "month": "2025-01-01",
                "block1": 105,
                "block2": 147,
                "block3": 103,
                "block4": 50,
                "block5": 0
            }
        ]
    }

    # Create calculator with injected data
    calculator = ElectricityBillCalculator(
        consumption_data=injected_consumption,
        pricelist_data=injected_pricelist,
        agreed_power_data=injected_agreed_power
    )
    
    # Mock monthly data from API
    monthly_data = {
        'readings': [
            {
                'readingType': READING_TYPE_VT,
                'consumption': 154.0  # 100 kWh VT consumption
            },
            {
                'readingType': READING_TYPE_MT,
                'consumption': 251.0   # 50 kWh MT consumption
            }
        ]
    }
    
    # Calculate bill for January 2025
    bill = calculator.calculate_bill(monthly_data, '2025-01-01')
    
    # Verify structure
    assert 'energyVT' in bill
    assert 'energyMT' in bill
    assert 'blockCosts' in bill
    assert 'totalBlockCost' in bill
    assert 'amount' in bill
    
    # VT: 154 * 0.084 = 12.936 → rounded to 12.94
    assert bill['energyVT'] == 12.94
    
    # MT: 251 * 0.07 = 17.57 → rounded to 17.57
    assert bill['energyMT'] == 17.57

    # Block totals with new agreed power values (5, 5.3, 5.6, 5.6, 5.6)
    # Each cost is rounded to 2 decimals BEFORE summing
    # Block1: round(18.0662,2) + round(2.0559,2) = 18.07 + 2.06 = 20.13
    # Block2: round(4.67672,2) + round(2.71068,2) = 4.68 + 2.71 = 7.39
    # Block3: round(1.071672,2) + round(1.89211,2) = 1.07 + 1.89 = 2.96
    # Block4: round(0.073696,2) + round(0.919,2) = 0.07 + 0.92 = 0.99
    # Block5: round(0,2) + round(0,2) = 0.00 + 0.00 = 0.00
    # Total: 31.47
    assert bill['totalBlockCost'] == 31.47
    
    # Additional costs: 0.37 + 0.62 + 1.99 + (-0.18) = 2.8
    assert 'additionalCosts' in bill
    assert bill['additionalCosts']['contributions'] == 0.37
    assert bill['additionalCosts']['exciseDuty'] == 0.62
    assert bill['additionalCosts']['monthlyAllowanceCost'] == 1.99
    assert bill['additionalCosts']['discount'] == -0.18
    assert bill['additionalCosts']['total'] == 2.8
    
    # Verify block costs exist
    for block_num in range(1, 6):
        block_key = f'block{block_num}'
        assert block_key in bill['blockCosts']
        assert 'agreedPowerCost' in bill['blockCosts'][block_key]
        assert 'consumptionCost' in bill['blockCosts'][block_key]
        assert 'total' in bill['blockCosts'][block_key]
    
    # Total should be energyVT + energyMT + totalBlockCost + additionalCosts.total
    # 12.94 + 17.57 + 31.47 + 2.8 = 64.78
    expected_total = bill['energyVT'] + bill['energyMT'] + bill['totalBlockCost'] + bill['additionalCosts']['total']
    assert bill['amount'] == expected_total
    assert bill['amount'] == 64.78
    
    print(f"✓ Bill calculation test with injected data passed")
    print(f"  Energy VT: €{bill['energyVT']}")
    print(f"  Energy MT: €{bill['energyMT']}")
    print(f"  Block Costs: €{bill['totalBlockCost']}")
    print(f"  Total: €{bill['amount']}")


def test_bill_calculation_father():
    """Test bill calculation with injected data (no file IO)."""
    # Inject custom pricelist, agreed power, and consumption data
    injected_pricelist = {
        "VT": 0.12479,
        "MT": 0.102850,
        "blocks": {
            "1": {"price": 0.019980, "agreedPowerPrice": 1.711260},
            "2": {"price": 0.018330, "agreedPowerPrice": 0.912240},
            "3": {"price": 0.018090, "agreedPowerPrice": 0.162970},
            "4": {"price": 0.018550, "agreedPowerPrice": 0.004070},
            "5": {"price": 0, "agreedPowerPrice": 0}
        },
        "additionalCosts": {
            "contributions": 1.71,
            "exciseDuty": 0.39,
            "monthlyAllowanceCost": 1.99,
            "discount": -1
        }
    }

    injected_agreed_power = {
        "agreements": [
            {
                "startDate": "2025-01-01",
                "endDate": "2025-12-31",
                "block1": 3.8,
                "block2": 3.9,
                "block3": 4.1,
                "block4": 4.1,
                "block5": 4.1
            }
        ]
    }

    injected_consumption = {
        "consumption": [
            {
                "month": "2025-01-01",
                "block1": 61,
                "block2": 89,
                "block3": 78,
                "block4": 29,
                "block5": 0
            }
        ]
    }

    # Create calculator with injected data
    calculator = ElectricityBillCalculator(
        consumption_data=injected_consumption,
        pricelist_data=injected_pricelist,
        agreed_power_data=injected_agreed_power
    )
    
    # Mock monthly data from API
    monthly_data = {
        'readings': [
            {
                'readingType': READING_TYPE_VT,
                'consumption': 120.0  # 100 kWh VT consumption
            },
            {
                'readingType': READING_TYPE_MT,
                'consumption': 137.0   # 50 kWh MT consumption
            }
        ]
    }
    
    # Calculate bill for January 2025
    bill = calculator.calculate_bill(monthly_data, '2025-01-01')
    
    # Verify structure
    assert 'energyVT' in bill
    assert 'energyMT' in bill
    assert 'blockCosts' in bill
    assert 'totalBlockCost' in bill
    assert 'amount' in bill
    
    # VT: 120 * 0.12479 = 14.9748 → rounded to 14.97
    assert bill['energyVT'] == 14.97
    
    # MT: 137 * 0.102850 = 14.09045 → rounded to 14.09
    assert bill['energyMT'] == 14.09

    # Block totals with new agreed power values (3.8, 3.9, 4.1, 4.1, 4.1)
    # Each cost is rounded to 2 decimals BEFORE summing
    # Block1: round(6.50279,2) + round(1.21878,2) = 6.50 + 1.22 = 7.72
    # Block2: round(3.55774,2) + round(1.63137,2) = 3.56 + 1.63 = 5.19
    # Block3: round(0.66817,2) + round(1.41102,2) = 0.67 + 1.41 = 2.08
    # Block4: round(0.01669,2) + round(0.53795,2) = 0.02 + 0.54 = 0.56
    # Block5: round(0,2) + round(0,2) = 0.00 + 0.00 = 0.00
    # Total: 15.55
    assert bill['totalBlockCost'] == 15.55
    
    # Additional costs: 1.71 + 0.39 + 1.99 + (-1) = 3.09
    assert 'additionalCosts' in bill
    assert bill['additionalCosts']['contributions'] == 1.71
    assert bill['additionalCosts']['exciseDuty'] == 0.39
    assert bill['additionalCosts']['monthlyAllowanceCost'] == 1.99
    assert bill['additionalCosts']['discount'] == -1
    assert bill['additionalCosts']['total'] == 3.09
    
    # Verify block costs exist
    for block_num in range(1, 6):
        block_key = f'block{block_num}'
        assert block_key in bill['blockCosts']
        assert 'agreedPowerCost' in bill['blockCosts'][block_key]
        assert 'consumptionCost' in bill['blockCosts'][block_key]
        assert 'total' in bill['blockCosts'][block_key]
    
    # Total should be energyVT + energyMT + totalBlockCost + additionalCosts.total
    # 14.97 + 14.09 + 15.55 + 3.09 = 47.70
    assert bill['amount'] == 47.70
    
    print(f"✓ Bill calculation test with injected data passed")
    print(f"  Energy VT: €{bill['energyVT']}")
    print(f"  Energy MT: €{bill['energyMT']}")
    print(f"  Block Costs: €{bill['totalBlockCost']}")
    print(f"  Total: €{bill['amount']}")


if __name__ == '__main__':
    test_bill_calculation_sister()
    test_bill_calculation_father()
