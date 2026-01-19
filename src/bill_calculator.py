"""Electricity bill calculator"""
import os
import json
from typing import Dict, Any
from datetime import datetime


class ElectricityBillCalculator:
    """Calculate electricity bill based on consumption data"""
    
    def __init__(self, consumption_file: str = None, pricelist_file: str = None, agreed_power_file: str = None,
                 consumption_data: Dict[str, Any] = None, pricelist_data: Dict[str, Any] = None,
                 agreed_power_data: Dict[str, Any] = None):
        """
        Initialize the bill calculator.
        
        Args:
            consumption_file: Path to JSON file with electricity consumption data
            pricelist_file: Path to JSON file with electricity pricelist
            agreed_power_file: Path to JSON file with agreed power data
        """
        self.consumption = {}
        self.pricelist = {}
        self.agreed_power = []
        
        # Default paths if files are not provided
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_consumption = os.path.join(current_dir, '..', 'data', 'consumption.json')
        default_pricelist = os.path.join(current_dir, '..', 'data', 'pricelist.json')
        default_agreed = os.path.join(current_dir, '..', 'data', 'agreed_power.json')
        
        consumption_path = consumption_file or default_consumption
        pricelist_path = pricelist_file or default_pricelist
        agreed_path = agreed_power_file or default_agreed
        
        # Prefer injected data when provided
        if consumption_data is not None:
            self.set_consumption_data(consumption_data)
        else:
            self.load_consumption(consumption_path)
        
        if pricelist_data is not None:
            self.set_pricelist_data(pricelist_data)
        else:
            self.load_pricelist(pricelist_path)
        
        if agreed_power_data is not None:
            self.set_agreed_power_data(agreed_power_data)
        else:
            self.load_agreed_power(agreed_path)
    
    def load_consumption(self, consumption_file: str):
        """
        Load consumption data from JSON file.
        
        Args:
            consumption_file: Path to JSON file with structure: {"consumption": [{"month": "YYYY-MM-DD", "block1": float, "block2": float, ...}]}
        """
        if not os.path.exists(consumption_file):
            raise FileNotFoundError(f"Consumption file not found: {consumption_file}")
        
        with open(consumption_file, 'r') as f:
            data = json.load(f)
        
        # Parse consumption into nested dict: {month: {block: amount, 'solar': amount}}
        for consumption_entry in data.get('consumption', []):
            month = consumption_entry['month']  # Format: YYYY-MM-DD (first day of month)
            
            if month not in self.consumption:
                self.consumption[month] = {}
            
            # Store each block value
            for key, value in consumption_entry.items():
                if key.startswith('block'):
                    block_num = int(key.replace('block', ''))
                    self.consumption[month][block_num] = float(value)
                elif key == 'usedElectricityFromSolar':
                    self.consumption[month]['solar'] = float(value)
    
    def load_pricelist(self, pricelist_file: str):
        """
        Load electricity pricelist from JSON file.
        
        Args:
            pricelist_file: Path to JSON file with structure: {"VT": float, "MT": float, "blocks": {"1": {"price": float, "agreedPowerPrice": float}}}
        """
        if not os.path.exists(pricelist_file):
            raise FileNotFoundError(f"Pricelist file not found: {pricelist_file}")
        
        with open(pricelist_file, 'r') as f:
            self.pricelist = json.load(f)

    def set_pricelist_data(self, pricelist: Dict[str, Any]):
        """Inject pricelist data directly (used for tests)."""
        self.pricelist = pricelist
    
    def load_agreed_power(self, agreed_power_file: str):
        """
        Load agreed power data from JSON file.
        
        Args:
            agreed_power_file: Path to JSON file with structure: {"agreements": [{"startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD", "block1": float, ...}]}
        """
        if not os.path.exists(agreed_power_file):
            raise FileNotFoundError(f"Agreed power file not found: {agreed_power_file}")
        
        with open(agreed_power_file, 'r') as f:
            data = json.load(f)
            self.agreed_power = data.get('agreements', [])

    def set_agreed_power_data(self, agreed_power: Dict[str, Any]):
        """Inject agreed power data directly (used for tests)."""
        self.agreed_power = agreed_power.get('agreements', [])
    
    def get_agreed_power_for_date(self, date: str) -> Dict[int, float]:
        """
        Get agreed power values for all blocks for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary mapping block numbers to agreed power (kW)
        """
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
        for agreement in self.agreed_power:
            start_date = datetime.strptime(agreement['startDate'], '%Y-%m-%d')
            end_date = datetime.strptime(agreement['endDate'], '%Y-%m-%d')
            
            if start_date <= date_obj <= end_date:
                # Found the right agreement period
                agreed_power_dict = {}
                for block_num in range(1, 6):
                    block_key = f'block{block_num}'
                    agreed_power_dict[block_num] = float(agreement[block_key])
                return agreed_power_dict
        
        raise ValueError(f"No agreed power data found for date {date}")
    
    def get_tariff_price(self, tariff_type: str) -> float:
        """
        Get tariff price (VT or MT).
        
        Args:
            tariff_type: 'VT' for Low Tariff or 'MT' for High Tariff
            
        Returns:
            Tariff price
        """
        if tariff_type not in self.pricelist:
            raise ValueError(f"Tariff type '{tariff_type}' not found in pricelist")
        return self.pricelist[tariff_type]

    def set_consumption_data(self, data: Dict[str, Any]):
        """
        Inject consumption data directly using same structure as JSON file.
        Expected structure: {"consumption": [{"month": "YYYY-MM-DD", "block1": float, ...}]}
        """
        self.consumption = {}
        for consumption_entry in data.get('consumption', []):
            month = consumption_entry['month']
            if month not in self.consumption:
                self.consumption[month] = {}
            for key, value in consumption_entry.items():
                if key.startswith('block'):
                    block_num = int(key.replace('block', ''))
                    self.consumption[month][block_num] = float(value)
                elif key == 'usedElectricityFromSolar':
                    self.consumption[month]['solar'] = float(value)
    
    def is_pricelist_valid_for_date(self, date: str) -> bool:
        """
        Check if the pricelist is valid for the given date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            True if pricelist is valid for the date, False otherwise
        """
        if 'validFrom' not in self.pricelist or 'validTo' not in self.pricelist:
            # If no validity dates specified, assume always valid
            return True
        
        valid_from = self.pricelist['validFrom']
        valid_to = self.pricelist['validTo']
        
        return valid_from <= date <= valid_to
    
    def get_block_prices(self, block: int) -> Dict[str, float]:
        """
        Get block prices (price and agreedPowerPrice).
        
        Args:
            block: Block number (1-5)
            
        Returns:
            Dictionary with 'price' and 'agreedPowerPrice'
        """
        block_str = str(block)
        if 'blocks' not in self.pricelist or block_str not in self.pricelist['blocks']:
            raise ValueError(f"Block {block} not found in pricelist")
        return self.pricelist['blocks'][block_str]
    
    def get_additional_costs(self) -> Dict[str, float]:
        """
        Get additional costs (contributions, excise duty, monthly allowance, discount).
        
        Returns:
            Dictionary with additional cost values
        """
        if 'additionalCosts' not in self.pricelist:
            return {
                'contributions': 0.0,
                'exciseDuty': 0.0,
                'monthlyAllowanceCost': 0.0,
                'discount': 0.0
            }
        return self.pricelist['additionalCosts']
    
    def get_consumption(self, date: str, block: int) -> float:
        """
        Get consumption amount for a specific date and block.
        
        Args:
            date: Date in YYYY-MM-DD format
            block: Block number (1-5)
            
        Returns:
            Consumption amount for the given date and block
        """
        # Extract month from date (YYYY-MM)
        month_key = date[:7] + '-01'
        
        # Try exact month first
        if month_key in self.consumption and block in self.consumption[month_key]:
            return self.consumption[month_key][block]
        
        # If month not found, try to find the most recent applicable consumption
        months = sorted([m for m in self.consumption.keys() if m <= month_key], reverse=True)
        if months:
            most_recent = months[0]
            if block in self.consumption[most_recent]:
                return self.consumption[most_recent][block]
        
        raise ValueError(f"No consumption data found for date {date} and block {block}")
    
    def calculate_bill(self, monthly_data: Dict[str, Any], month_date: str) -> Dict[str, Any]:
        """
        Calculate electricity bill from monthly consumption data.
        
        Formula:
        - EnergyVT = VT consumption * VT price
        - EnergyMT = MT consumption * MT price
        - For each block:
            - Agreed power cost = agreed kW * agreedPowerPrice
            - Consumption cost = energy consumed * block price
        - Total = EnergyVT + EnergyMT + sum(all block costs)
        
        Args:
            monthly_data: Processed monthly consumption data with readings from API
            month_date: Date string in YYYY-MM-DD format for the month
            
        Returns:
            Dictionary containing bill calculation details
        """
        from constants import READING_TYPE_VT, READING_TYPE_MT
        
        # Validate pricelist is valid for the given date
        if not self.is_pricelist_valid_for_date(month_date):
            raise ValueError(f"Pricelist is not valid for date {month_date}. Valid range: {self.pricelist.get('validFrom', 'N/A')} to {self.pricelist.get('validTo', 'N/A')}")
        
        # Initialize costs
        energy_vt = 0.0
        energy_mt = 0.0
        vt_consumption = 0.0
        mt_consumption = 0.0
        
        # Extract VT and MT consumption from API readings
        for reading in monthly_data.get('readings', []):
            reading_type = reading.get('readingType')
            consumption = reading.get('consumption', 0.0)
            
            if reading_type == READING_TYPE_VT:
                vt_consumption = consumption
            elif reading_type == READING_TYPE_MT:
                mt_consumption = consumption
        
        # Get solar electricity for this month
        month_key = month_date[:7] + '-01'
        solar_electricity = 0.0
        if month_key in self.consumption and 'solar' in self.consumption[month_key]:
            solar_electricity = self.consumption[month_key]['solar']
        
        # Distribute solar electricity proportionally to VT and MT
        total_consumption = vt_consumption + mt_consumption
        if total_consumption > 0 and solar_electricity > 0:
            vt_proportion = vt_consumption / total_consumption
            mt_proportion = mt_consumption / total_consumption
            
            vt_consumption += solar_electricity * vt_proportion
            mt_consumption += solar_electricity * mt_proportion
        
        # Calculate VT and MT energy costs
        energy_vt = vt_consumption * self.get_tariff_price('VT')
        energy_mt = mt_consumption * self.get_tariff_price('MT')
        
        # Calculate block costs
        block_costs = {}
        total_block_cost = 0.0
        
        # Get agreed power for this month
        agreed_powers = self.get_agreed_power_for_date(month_date)
        
        for block_num in range(1, 6):
            # Get block pricing
            block_prices = self.get_block_prices(block_num)
            
            # Get agreed power for this block
            agreed_kw = agreed_powers.get(block_num, 0.0)
            
            # Get consumption for this block from consumption.json
            consumption_kwh = self.get_consumption(month_date, block_num)
            
            # Add solar electricity to block 1
            if block_num == 1 and solar_electricity > 0:
                consumption_kwh += solar_electricity
            
            # Calculate costs - round each before summing
            agreed_power_cost = round(agreed_kw * block_prices['agreedPowerPrice'], 2)
            consumption_cost = round(consumption_kwh * block_prices['price'], 2)
            block_total = agreed_power_cost + consumption_cost
            
            block_costs[f'block{block_num}'] = {
                'agreedPowerCost': agreed_power_cost,
                'consumptionCost': consumption_cost,
                'total': block_total
            }
            
            total_block_cost += block_total
        
        # Get additional costs
        additional_costs = self.get_additional_costs()
        contributions = additional_costs.get('contributions', 0.0)
        excise_duty = additional_costs.get('exciseDuty', 0.0)
        monthly_allowance = additional_costs.get('monthlyAllowanceCost', 0.0)
        discount = additional_costs.get('discount', 0.0)
        
        total_additional = contributions + excise_duty + monthly_allowance + discount
        
        # Round each component to 2 decimals first
        energy_vt_rounded = round(energy_vt, 2)
        energy_mt_rounded = round(energy_mt, 2)
        total_block_cost_rounded = round(total_block_cost, 2)
        total_additional_rounded = round(total_additional, 2)
        
        # Calculate total from rounded components
        total_amount = energy_vt_rounded + energy_mt_rounded + total_block_cost_rounded + total_additional_rounded
        
        # Calculate total energy used (VT + MT consumption including solar)
        total_energy_used = round(vt_consumption + mt_consumption, 2)
        
        return {
            'energyVT': energy_vt_rounded,
            'energyMT': energy_mt_rounded,
            'totalEnergyUsed': total_energy_used,
            'blockCosts': block_costs,
            'totalBlockCost': total_block_cost_rounded,
            'additionalCosts': {
                'contributions': round(contributions, 2),
                'exciseDuty': round(excise_duty, 2),
                'monthlyAllowanceCost': round(monthly_allowance, 2),
                'discount': round(discount, 2),
                'total': total_additional_rounded
            },
            'amount': round(total_amount, 2)
        }
    
    def calculate_annual_bill(self, annual_data: Dict[str, Dict[str, Any]], year: int) -> Dict[str, Any]:
        """
        Calculate annual electricity bill.
        
        Args:
            annual_data: Dictionary with month names as keys and consumption data as values
            year: Year for which to calculate the bill
            
        Returns:
            Dictionary containing total annual bill and monthly breakdown
        """
        annual_bill = {
            'monthly_bills': {},
            'total_amount': 0.0
        }
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        for idx, (month_name, data) in enumerate(annual_data.items()):
            # Create date string for first day of month
            month_num = month_names.index(month_name) + 1 if month_name in month_names else idx + 1
            month_date = f"{year}-{month_num:02d}-01"
            
            monthly_bill = self.calculate_bill(data, month_date)
            annual_bill['monthly_bills'][month_name] = monthly_bill
            annual_bill['total_amount'] += monthly_bill['amount']
        
        # Round total to 2 decimals
        annual_bill['total_amount'] = round(annual_bill['total_amount'], 2)
        
        return annual_bill

