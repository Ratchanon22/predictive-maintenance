import pandas as pd
import numpy as np
import re
import os

def parse_vibration_file(file_path):
    """Reads the vibration file and extracts Header and Amplitude data."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Extract Header info using Regex
    equipment = re.search(r"Equipment:\s+(.*)", content).group(1).strip()
    date_str = re.search(r"Date/Time:\s+(\d{2}-\w{3}-\d{2}\s+\d{2}:\d{2}:\d{2})", content).group(1)
    
    # Extract Amplitude values starting from line 8
    table_data = []
    lines = content.split('\n')
    for line in lines[8:]: 
        values = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        if len(values) >= 2:
            # Collect Amplitudes (odd indices)
            amps = [float(values[i]) for i in range(1, len(values), 2)]
            table_data.extend(amps)

    return {
        'Equipment': equipment,
        'Timestamp': pd.to_datetime(date_str),
        'Amplitudes': np.array(table_data)
    }

def calculate_rms(amplitudes):
    """Calculates the Root Mean Square (RMS) value."""
    if len(amplitudes) == 0:
        return 0
    return np.sqrt(np.mean(np.square(amplitudes)))

if __name__ == "__main__":
    data_dir = "./data"
    print("-" * 50)
    print("Step 1 Test: Automatic File Discovery")
    print("-" * 50)
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory '{data_dir}' not found.")
    else:
        files = os.listdir(data_dir)
        txt_files = [f for f in files if f.endswith('.txt')]
        print(f"Found {len(txt_files)} files in the data folder.")
        
        if len(txt_files) > 0:
            test_file_path = os.path.join(data_dir, txt_files[0])
            print(f"\nAttempting to read: {test_file_path}")
            try:
                data = parse_vibration_file(test_file_path)
                rms_value = calculate_rms(data['Amplitudes'])
                print(f"✅ File parsed successfully!")
                print(f"📌 Equipment: {data['Equipment']}")
                print(f"🕒 Timestamp: {data['Timestamp']}")
                print(f"📊 Data Points: {len(data['Amplitudes']):,}")
                print(f"📈 Calculated RMS: {rms_value:.4f}")
            except Exception as e:
                print(f"❌ Error parsing file: {e}")
        else:
            print("❌ No .txt files found in the data folder.")