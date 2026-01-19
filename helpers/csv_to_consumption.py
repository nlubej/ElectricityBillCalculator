"""Helper script to convert CSV consumption data to consumption.json format"""
import csv
import json
import sys
import re
from pathlib import Path
from datetime import datetime


def parse_monthly_csv_folder(folder_path: str, output_file: str = None, solar_data: dict = None):
    """
    Parse folder with monthly CSV files containing daily consumption by block.
    Sums up daily values for each block to get monthly totals.
    
    Expected CSV format (one file per month):
    Datum,Prejeta delovna energija v časovnem bloku 1 [kWh],...,Skupaj
    2025-01-01,0.00,13.8120,7.7880,16.8390,0.00,38.4390
    2025-01-02,0.00,11.6510,6.4320,8.7490,0.00,26.8320
    ...
    
    Args:
        folder_path: Path to folder containing monthly CSV files
        output_file: Path to output JSON file (default: data/consumption.json)
        solar_data: Optional dict with month: solar_value mapping
    """
    # Default output path
    if output_file is None:
        script_dir = Path(__file__).parent
        output_file = script_dir.parent / 'data' / 'consumption.json'
    
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder not found: {folder_path}")
    
    consumption_data = {"consumption": []}
    csv_files = sorted(folder.glob("*.csv"))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {folder_path}")
    
    for csv_file in csv_files:
        # Extract date from filename (e.g., 2025-01-01 from "...-2025-01-01-2025-01-31.csv")
        match = re.search(r'(\d{4}-\d{2}-\d{2})', csv_file.name)
        if not match:
            print(f"Warning: Could not extract date from filename: {csv_file.name}")
            continue
        
        month_date = match.group(1)
        
        # Initialize block sums
        block_sums = {
            'block1': 0.0,
            'block2': 0.0,
            'block3': 0.0,
            'block4': 0.0,
            'block5': 0.0
        }
        
        # Read and sum daily values
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Map CSV columns to blocks (assuming they appear in order 1-5)
                    # Column format: "Prejeta delovna energija v časovnem bloku X [kWh]"
                    for i in range(1, 6):
                        col_name = f'Prejeta delovna energija v časovnem bloku {i} [kWh]'
                        if col_name in row:
                            try:
                                value = float(row[col_name].replace(',', '.'))
                                block_sums[f'block{i}'] += value
                            except (ValueError, KeyError):
                                continue
            
            # Get solar data for this month if provided
            solar_value = 0.0
            if solar_data and month_date in solar_data:
                solar_value = solar_data[month_date]
            
            entry = {
                "month": month_date,
                "block1": round(block_sums['block1'], 2),
                "block2": round(block_sums['block2'], 2),
                "block3": round(block_sums['block3'], 2),
                "block4": round(block_sums['block4'], 2),
                "block5": round(block_sums['block5'], 2),
                "usedElectricityFromSolar": solar_value
            }
            
            consumption_data['consumption'].append(entry)
            print(f"✓ Processed {csv_file.name}: {sum(block_sums.values()):.2f} kWh total")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")
            continue
    
    # Sort by month
    consumption_data['consumption'].sort(key=lambda x: x['month'])
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consumption_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Successfully converted {len(consumption_data['consumption'])} months")
    print(f"  Output saved to: {output_file}")
    
    return consumption_data


def csv_to_consumption_json(csv_file: str, output_file: str = None):
    """
    Convert CSV file with monthly consumption data to consumption.json format.
    
    Expected CSV format:
    month,block1,block2,block3,block4,block5,usedElectricityFromSolar
    2025-01-01,105.5,147.3,103.2,50.1,0.0,25.5
    2025-02-01,110.2,150.4,105.6,52.3,0.0,30.2
    ...
    
    Args:
        csv_file: Path to input CSV file
        output_file: Path to output JSON file (default: data/consumption.json)
    """
    # Default output path
    if output_file is None:
        script_dir = Path(__file__).parent
        output_file = script_dir.parent / 'data' / 'consumption.json'
    
    consumption_data = {"consumption": []}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            required_fields = ['month', 'block1', 'block2', 'block3', 'block4', 'block5']
            optional_fields = ['usedElectricityFromSolar']
            
            if not all(field in reader.fieldnames for field in required_fields):
                raise ValueError(f"CSV must contain columns: {', '.join(required_fields)}")
            
            for row in reader:
                # Validate date format
                try:
                    datetime.strptime(row['month'], '%Y-%m-%d')
                except ValueError:
                    print(f"Warning: Invalid date format '{row['month']}', expected YYYY-MM-DD")
                    continue
                
                entry = {
                    "month": row['month'],
                    "block1": float(row['block1']),
                    "block2": float(row['block2']),
                    "block3": float(row['block3']),
                    "block4": float(row['block4']),
                    "block5": float(row['block5']),
                    "usedElectricityFromSolar": float(row.get('usedElectricityFromSolar', 0.0))
                }
                
                consumption_data['consumption'].append(entry)
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consumption_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully converted {len(consumption_data['consumption'])} entries")
        print(f"  Output saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV: {e}")
        sys.exit(1)


def create_sample_csv(output_file: str = "consumption_sample.csv"):
    """
    Create a sample CSV file to demonstrate the expected format.
    
    Args:
        output_file: Path to output sample CSV file
    """
    sample_data = [
        ["month", "block1", "block2", "block3", "block4", "block5", "usedElectricityFromSolar"],
        ["2025-01-01", "105.5", "147.3", "103.2", "50.1", "0.0", "25.5"],
        ["2025-02-01", "110.2", "150.4", "105.6", "52.3", "0.0", "30.2"],
        ["2025-03-01", "108.8", "148.9", "104.1", "51.2", "0.0", "35.8"],
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)
    
    print(f"✓ Sample CSV created: {output_file}")
    print(f"  Edit this file with your consumption data and run:")
    print(f"  python helpers/csv_to_consumption.py {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Convert folder with monthly CSV files (daily data summed by block):")
        print("    python helpers/csv_to_consumption.py --folder data/monthly-consumption-by-block [output.json]")
        print()
        print("  Convert single CSV file with monthly totals:")
        print("    python helpers/csv_to_consumption.py input.csv [output.json]")
        print()
        print("  Create sample CSV:")
        print("    python helpers/csv_to_consumption.py --sample [output.csv]")
        sys.exit(1)
    
    if sys.argv[1] == '--sample':
        sample_file = sys.argv[2] if len(sys.argv) > 2 else "consumption_sample.csv"
        create_sample_csv(sample_file)
    elif sys.argv[1] == '--folder':
        if len(sys.argv) < 3:
            print("Error: Folder path required")
            sys.exit(1)
        folder_path = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        parse_monthly_csv_folder(folder_path, output_file)
    else:
        csv_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        csv_to_consumption_json(csv_file, output_file)
