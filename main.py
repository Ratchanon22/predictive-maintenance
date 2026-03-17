import os
import sys
import argparse
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processor import parse_vibration_file, calculate_velocity_rms
from analyzer import ISOAnalyzer
from predictor import VibrationPredictor

parser = argparse.ArgumentParser()
parser.add_argument("--data",       default="./data")
parser.add_argument("--output",     default="./output_plots")
parser.add_argument("--group",      default="group2", choices=["group1", "group2"])
parser.add_argument("--foundation", default="rigid",  choices=["rigid", "flexible"])
parser.add_argument("--target",     default="2024-11-15")
args = parser.parse_args()

DATA_DIR    = args.data
PLOTS_DIR   = args.output
TARGET_DATE = args.target

analyzer  = ISOAnalyzer(machinery_group=args.group, foundation=args.foundation)
predictor = VibrationPredictor(zone_limits=analyzer.thresholds + [analyzer.thresholds[-1] * 1.5])


def run():
    print("=" * 90)
    print(f"  VIBRATION FORECAST SYSTEM  |  Target: {TARGET_DATE}")
    print(f"  ISO 10816-3 Config: {analyzer.boundary_labels}")
    print("=" * 90)

    if not os.path.exists(DATA_DIR):
        print(f"ไม่พบโฟลเดอร์ '{DATA_DIR}'")
        return

    txt_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt"))
    if not txt_files:
        print(f"ไม่พบไฟล์ .txt ใน '{DATA_DIR}'")
        return

    print(f"พบไฟล์ทั้งหมด {len(txt_files)} ไฟล์ใน '{DATA_DIR}'\n")

    records = []
    for fname in txt_files:
        data = parse_vibration_file(os.path.join(DATA_DIR, fname))
        if data is None:
            continue
        v_rms = calculate_velocity_rms(data["Times_ms"], data["Amplitudes"])
        records.append({
            "Equipment": data["Equipment"],
            "Date":      data["Timestamp"],
            "RMS_mms":   v_rms,
        })

    if not records:
        print("ไม่มีข้อมูลที่ใช้ได้เลย")
        return

    df = pd.DataFrame(records).sort_values("Date")

    print(f"{'Equipment':<38} {'Date':<22} {'Velocity RMS (mm/s)':>20}  Zone")
    print("-" * 90)
    for _, row in df.iterrows():
        z = analyzer.classify(row["RMS_mms"])
        print(f"  {row['Equipment']:<36} {str(row['Date']):<22} {row['RMS_mms']:>18.3f}  {z.color_emoji} {z.label}")

    print("\n" + "=" * 90)
    print(f"  FORECAST → {TARGET_DATE}")
    print("=" * 90)

    report_rows = []
    for eq in df["Equipment"].unique():
        eq_df = df[df["Equipment"] == eq].sort_values("Date")
        latest_rms   = eq_df.iloc[-1]["RMS_mms"]
        current_zone = analyzer.classify(latest_rms)

        trend, pred_rms = predictor.predict_target_date_and_plot(
            dates           = eq_df["Date"].tolist(),
            rms_values      = eq_df["RMS_mms"].tolist(),
            equipment_name  = eq,
            target_date_str = TARGET_DATE,
            save_dir        = PLOTS_DIR,
        )

        if pred_rms is not None:
            forecast_zone = analyzer.classify(pred_rms)
            print(f"\n  {eq}")
            print(f"    ปัจจุบัน    : {latest_rms:.3f} mm/s  → {current_zone.color_emoji} Zone {current_zone.label} ({current_zone.name})")
            print(f"    Trend       : {trend}")
            print(f"    พยากรณ์     : {pred_rms:.3f} mm/s  → {forecast_zone.color_emoji} Zone {forecast_zone.label} ({forecast_zone.name})")
            print(f"    บันทึก plot : {eq.replace(' ', '_')}_forecast_plot.png")

            report_rows.append({
                "Machine Name":                    eq,
                "Current RMS (mm/s)":              f"{latest_rms:.3f}",
                "Current Zone":                    f"Zone {current_zone.label} - {current_zone.name}",
                f"Forecast RMS ({TARGET_DATE})":   f"{pred_rms:.3f}",
                "Forecast Zone":                   f"Zone {forecast_zone.label} - {forecast_zone.name}",
                "Trend":                           trend,
            })
        else:
            print(f"\n  {eq}: ข้อมูลไม่พอสำหรับการพยากรณ์")

    if report_rows:
        report_df = pd.DataFrame(report_rows)
        print("\n" + "-" * 90)
        print("  สรุปผลการพยากรณ์")
        print("-" * 90)
        print(report_df.to_string(index=False))
        print("-" * 90)

        csv_path = "maintenance_forecast_report.csv"
        report_df.to_csv(csv_path, index=False)
        print(f"\n  บันทึก CSV → '{csv_path}'")
        print(f"  บันทึก plots → '{PLOTS_DIR}/'")


if __name__ == "__main__":
    run()
