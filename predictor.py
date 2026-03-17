import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression


class VibrationPredictor:
    def __init__(self, zone_limits=None):
        self.zone_limits = zone_limits or [1.4, 2.8, 4.5, 7.1]

    def predict_target_date_and_plot(self, dates, rms_values, equipment_name,
                                     target_date_str="2024-11-15", save_dir="./output_plots"):
        if len(dates) < 2:
            return "[NO_DATA]", None

        os.makedirs(save_dir, exist_ok=True)

        # fit linear regression
        X = np.array([d.toordinal() for d in dates]).reshape(-1, 1)
        y = np.array(rms_values)
        model = LinearRegression()
        model.fit(X, y)
        slope = float(model.coef_[0])

        target_date = pd.to_datetime(target_date_str)
        predicted_rms = max(float(model.predict([[target_date.toordinal()]])[0]), 0.0)

        # ประเมิน trend
        if slope > 0.05:
            trend = "[DANGER]"
        elif slope > 0:
            trend = "[WARNING]"
        elif slope > -0.05:
            trend = "[STABLE]"
        else:
            trend = "[IMPROVING]"

        # สร้าง timeline สำหรับ plot
        plot_dates = list(dates)
        if target_date > dates[-1]:
            plot_dates.append(target_date)
        X_plot = np.array([d.toordinal() for d in plot_dates]).reshape(-1, 1)
        y_plot = np.maximum(model.predict(X_plot), 0)

        # วาดกราฟ
        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        # zone bands
        zone_colors = ["#00c89630", "#a8d40030", "#ffb80040", "#ff3c3c35"]
        y_max = max(max(rms_values) * 1.4, predicted_rms * 1.3, self.zone_limits[-1] * 1.2)
        limits = [0] + list(self.zone_limits) + [y_max]
        for i in range(4):
            ax.axhspan(limits[i], limits[i + 1], color=zone_colors[i], zorder=0)

        # เส้นขอบ zone
        zcolors = ["#00c896", "#a8d400", "#ffb800", "#ff3c3c"]
        for lim, col in zip(self.zone_limits, zcolors):
            ax.axhline(lim, color=col, linewidth=0.8, linestyle="--", alpha=0.7, zorder=1)

        # ข้อมูลจริง
        ax.plot(dates, rms_values, marker="o", markersize=9, linewidth=2,
                color="#00c8ff", label="Historical RMS (mm/s)", zorder=4)

        # เส้น forecast
        ax.plot(plot_dates, y_plot, linewidth=1.5, linestyle="--",
                color="#000000", alpha=0.95, label=f"Linear Forecast ({trend})", zorder=3)

        # ดาว forecast
        ax.scatter(target_date, predicted_rms, marker="*", s=280,
                   color="#ffdd00", edgecolors="#000000", linewidths=1.2,
                   label=f"Forecast {target_date_str}: {predicted_rms:.3f} mm/s", zorder=5)

        ax.annotate(f" {predicted_rms:.3f} mm/s", xy=(target_date, predicted_rms),
                    color="#333333", fontsize=9, va="center")

        ax.set_title(f"Vibration Forecast Analysis: {equipment_name}",
                     color="black", fontsize=13, fontweight="bold", pad=14)
        ax.set_xlabel("Timeline", color="#333333", fontsize=10)
        ax.set_ylabel("Velocity RMS (mm/s)", color="#333333", fontsize=10)
        ax.tick_params(colors="#333333")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b-%y"))
        fig.autofmt_xdate()
        for spine in ax.spines.values():
            spine.set_edgecolor("#cccccc")
        ax.grid(color="#e0e0e0", linestyle="--", linewidth=0.5, zorder=0)
        ax.set_ylim(0, y_max)
        ax.legend(facecolor="white", edgecolor="#cccccc", labelcolor="#333333", fontsize=9)

        # label zone
        zone_mids = [
            (0 + self.zone_limits[0]) / 2,
            (self.zone_limits[0] + self.zone_limits[1]) / 2,
            (self.zone_limits[1] + self.zone_limits[2]) / 2,
            (self.zone_limits[2] + y_max * 0.9) / 2,
        ]
        for mid, txt, col in zip(zone_mids, ["ZONE A", "ZONE B", "ZONE C", "ZONE D"], zcolors):
            if mid < y_max:
                ax.text(plot_dates[-1], mid, f" {txt}", color=col,
                        fontsize=8, va="center", fontweight="bold", alpha=1.0)

        plt.tight_layout()
        safe_name = str(equipment_name).replace(" ", "_").replace("/", "_").replace(".", "")
        plt.savefig(os.path.join(save_dir, f"{safe_name}_forecast_plot.png"), dpi=150, facecolor="white")
        plt.close()

        return trend, predicted_rms


if __name__ == "__main__":
    predictor = VibrationPredictor(zone_limits=[1.4, 2.8, 4.5, 7.1])

    dates = [pd.Timestamp("2024-06-28"), pd.Timestamp("2024-09-04"), pd.Timestamp("2024-10-16")]
    rms = [7.719, 5.765, 6.089]

    trend, pred = predictor.predict_target_date_and_plot(dates, rms, "Jockey Pump", "2024-11-15")
    print(f"trend={trend}, forecast={pred:.3f} mm/s")
