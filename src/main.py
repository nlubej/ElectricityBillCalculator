"""Main application entry point"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from api_client import ElectricDataAPIClient
from constants import READING_TYPE_VT, READING_TYPE_MT
from data_processor import process_meter_readings
from bill_calculator import ElectricityBillCalculator


def get_month_ranges(year: int):
    """Generate date ranges for each month of a year (first day to first day of next month)"""
    months = []
    for month in range(1, 13):
        start_date = datetime(year, month, 1)
        
        # Calculate next month's first day
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        months.append({
            'month': month,
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        })
    
    return months


def main():
    """Main application function"""
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Initialize API client and bill calculator
        client = ElectricDataAPIClient()
        calculator = ElectricityBillCalculator()
        
        # Configuration
        usage_point = "3-256908"
        reading_types = [READING_TYPE_VT, READING_TYPE_MT]
        year = 2025
        
        print(f"Calculating electricity bill for {year}")
        print(f"Usage Point: {usage_point}\n")
        
        # Get all monthly ranges for 2025
        month_ranges = get_month_ranges(year)
        
        all_results = {}
        
        # Call API for each month
        for month_data in month_ranges:
            month = month_data['month']
            start_time = month_data['start']
            end_time = month_data['end']
            
            month_name = datetime.strptime(f"{year}-{month:02d}-01", '%Y-%m-%d').strftime('%B')
            
            try:
                # Get raw data
                data = client.get_electric_data(usage_point, start_time, end_time, reading_types)
                
                # Process data
                processed_data = process_meter_readings(data)
                all_results[month_name] = processed_data
                
            except Exception as e:
                print(f"Error retrieving data for {month_name}: {e}")
        
        # Calculate bill
        bill = calculator.calculate_annual_bill(all_results, year)
        
        # Display results
        print(f"\nAnnual Bill Summary for {year}")
        print(f"{'='*50}")
        
        for month_name, monthly_bill in bill['monthly_bills'].items():
            print(f"\n{month_name}:")
            print(f"  Total Energy Used: {monthly_bill['totalEnergyUsed']} kWh")
            print(f"  Energy VT: €{monthly_bill['energyVT']}")
            print(f"  Energy MT: €{monthly_bill['energyMT']}")
            print(f"  Block Costs: €{monthly_bill['totalBlockCost']}")
            print(f"  Total: €{monthly_bill['amount']}")
        
        print(f"\n{'='*50}")
        print(f"Total Annual Bill: €{bill['total_amount']}")
        print(f"{'='*50}")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
