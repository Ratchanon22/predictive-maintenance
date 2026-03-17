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
        latest_rms = rms_values[-1]
        
        if latest_rms >= self.red_limit:
            return "[FAILED]", None
        if len(dates) < 2:
            return "[NO_DATA]", None

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        x_days = np.array([d.toordinal() for d in dates]).reshape(-1, 1)
        y_rms = np.array(rms_values)
        self.model.fit(x_days, y_rms)
        slope = self.model.coef_[0]
        intercept = self.model.intercept_

        plt.figure(figsize=(10, 5))
        plt.plot(dates, y_rms, marker='o', label='Actual RMS')

        if slope > 0:
            days_to_red = (self.red_limit - intercept) / slope
            fail_date = datetime.date.fromordinal(int(days_to_red))
            trend_msg = "[DANGER]"
            
            future_dates = pd.date_range(start=dates[0], end=fail_date)
            plt.plot(future_dates, self.model.predict(np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)), '--r', label='Trend')
        else:
            fail_date = None
            trend_msg = "[STABLE]"

        plt.title(f'Analysis: {equipment_name}')
        plt.savefig(os.path.join(save_dir, f"{equipment_name}_plot.png"))
        plt.close()

        return trend_msg, fail_date
