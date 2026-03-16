import os
import pandas as pd
from processor import parse_vibration_file, calculate_rms
from analyzer import ISOAnalyzer
from predictor import VibrationPredictor

def run_system():
    data_dir = "./data"
    plots_dir = "./output_plots"
    
    print("=" * 75)
    print("VIBRATION PREDICTIVE MAINTENANCE SYSTEM (ISO 10816-3)")
    print("=" * 75)

    all_data = []
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found.")
        return

    txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    print(f"Processing {len(txt_files)} files... Generating analysis and plots.\n")

    for file_name in txt_files:
        file_path = os.path.join(data_dir, file_name)
        try:
            parsed_data = parse_vibration_file(file_path)
            rms = calculate_rms(parsed_data['Amplitudes'])
            all_data.append({
                'Equipment': parsed_data['Equipment'],
                'Date': parsed_data['Timestamp'],
                'RMS_Value': rms
            })
        except Exception:
            pass

    df = pd.DataFrame(all_data)
    analyzer = ISOAnalyzer()
    predictor = VibrationPredictor()
    report = []

    unique_equipments = df['Equipment'].unique()
    
    for eq in unique_equipments:
        eq_data = df[df['Equipment'] == eq].sort_values('Date')
        latest_rms = eq_data.iloc[-1]['RMS_Value']
        latest_date = eq_data.iloc[-1]['Date']
        
        current_status = analyzer.classify_status(latest_rms)
        dates_list = eq_data['Date'].tolist()
        rms_list = eq_data['RMS_Value'].tolist()
        
        trend, fail_date = predictor.predict_rul_and_plot(dates_list, rms_list, eq, plots_dir)
        fail_date_str = fail_date.strftime('%d-%b-%Y') if fail_date else "N/A"
        
        report.append({
            'Machine Name': eq,
            'Latest Date': latest_date.strftime('%d-%b-%Y'),
            'RMS': f"{latest_rms:.4f}",
            'Status': current_status.split(' ')[0],
            'Trend': trend.split(' ')[0],
            'Est. Failure': fail_date_str
        })

    report_df = pd.DataFrame(report)
    print("-" * 85)
    print("EXECUTIVE SUMMARY REPORT")
    print("-" * 85)
    print(report_df.to_string(index=False))
    print("-" * 85)
    
    report_df.to_csv("maintenance_report.csv", index=False)
    print("💾 Summary report saved to 'maintenance_report.csv'")
    print(f"📈 Trend plots generated successfully in '{plots_dir}'")

if __name__ == "__main__":
    run_system()