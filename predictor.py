import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
import matplotlib.pyplot as plt
import os

class VibrationPredictor:
    def __init__(self, red_limit=7.1):
        self.red_limit = red_limit
        self.model = LinearRegression()

    def predict_rul_and_plot(self, dates, rms_values, equipment_name, save_dir="./output_plots"):
        """Predicts failure date and generates a trend analysis graph."""
        if len(dates) < 2:
            return "[INFO] Insufficient Data", None

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        x_days = np.array([d.toordinal() for d in dates]).reshape(-1, 1)
        y_rms = np.array(rms_values)
        self.model.fit(x_days, y_rms)
        slope = self.model.coef_[0]
        intercept = self.model.intercept_

        plt.figure(figsize=(10, 5))
        plt.plot(dates, y_rms, marker='o', markersize=8, linestyle='-', color='#1f77b4', label='Actual RMS (Measured)')

        if slope > 0:
            days_to_red = (self.red_limit - intercept) / slope
            fail_date = datetime.date.fromordinal(int(days_to_red))
            trend_msg = "[DANGER] Degrading Trend"
            
            future_dates = pd.date_range(start=dates[0], end=fail_date)
            future_x = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
            future_y = self.model.predict(future_x)
            
            plt.plot(future_dates, future_y, linestyle='--', color='#d62728', label='Prediction Trend')
            plt.axvline(x=pd.to_datetime(fail_date), color='purple', linestyle='-.', label=f'Est. Failure: {fail_date.strftime("%d-%b-%Y")}')
        else:
            fail_date = None
            trend_msg = "[SAFE] Stable Trend"
            trend_y = self.model.predict(x_days)
            plt.plot(dates, trend_y, linestyle='--', color='#2ca02c', label='Trend Line')

        plt.axhline(y=self.red_limit, color='red', linestyle='-', linewidth=2, label='Danger Limit (ISO 7.1 RMS)')
        plt.title(f'Vibration Trend Analysis: {equipment_name}', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Vibration RMS (mm/s)')
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.tight_layout()

        safe_name = str(equipment_name).replace("/", "_").replace("\\", "_").replace(" ", "_")
        plot_path = os.path.join(save_dir, f"{safe_name}_trend.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()

        return trend_msg, fail_date