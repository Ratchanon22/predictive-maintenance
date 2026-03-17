import re
import numpy as np
import pandas as pd
from scipy import signal

MAX_ACCEL_G = 10.0
G_TO_MS2 = 9.81


def parse_vibration_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    eq_match = re.search(r"Equipment:\s+(.*)", content)
    dt_match = re.search(r"Date/Time:\s+(\d{2}-\w{3}-\d{2}\s+\d{2}:\d{2}:\d{2})", content)

    if not eq_match or not dt_match:
        print(f"  ⚠ อ่าน header ไม่ได้: {file_path}")
        return None

    equipment = eq_match.group(1).strip().replace("(CHPP) ", "")
    timestamp = pd.to_datetime(dt_match.group(1), dayfirst=True)

    # แก้ scientific notation ที่ format ผิด เช่น 7.2-5 → 7.2e-5
    content = re.sub(r"(\d+\.\d+)([-+])(\d)\b", r"\1e\2\3", content)

    lines = content.split("\n")
    times, amps = [], []
    started = False

    for line in lines:
        if "---" in line:
            started = True
            continue
        if not started:
            continue
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
        for i in range(0, len(nums) - 1, 2):
            try:
                t = float(nums[i])
                a = float(nums[i + 1])
                if t >= 0:
                    times.append(t)
                    amps.append(a)
            except ValueError:
                pass

    if len(times) < 64:
        print(f"  ⚠ ข้อมูลน้อยเกินไป: {file_path} ({len(times)} samples)")
        return None

    times = np.array(times)
    amps = np.array(amps)

    # เรียงตาม time
    idx = np.argsort(times)
    times, amps = times[idx], amps[idx]

    # ตัดค่าที่ผิดปกติออก
    valid = np.abs(amps) < MAX_ACCEL_G
    removed = len(amps) - valid.sum()
    if removed > 0:
        print(f"  🔧 ลบ {removed} sample ที่ผิดปกติ (|a| >= {MAX_ACCEL_G} G) จาก {file_path}")
    times, amps = times[valid], amps[valid]

    return {
        "Equipment": equipment,
        "Timestamp": timestamp,
        "Times_ms": times,
        "Amplitudes": amps,
    }


def calculate_velocity_rms(times_ms, accel_g):
    t_s = times_ms * 1e-3
    a_ms2 = accel_g * G_TO_MS2
    a_ms2 -= a_ms2.mean()

    # หา sampling rate จาก median ของช่วงเวลา
    dt_vals = np.diff(t_s)
    dt = float(np.median(dt_vals[dt_vals > 0]))
    if dt <= 0 or np.isnan(dt):
        return 0.0
    fs = 1.0 / dt

    # interpolate ให้ได้ uniform grid
    t_uni = np.arange(t_s[0], t_s[-1], dt)
    a_uni = np.interp(t_uni, t_s, a_ms2)

    # bandpass filter 10-1000 Hz ตาม ISO
    f_high = min(1000.0, fs * 0.45)
    if f_high <= 10.0:
        sos = signal.butter(4, 10.0 / (fs / 2), btype="highpass", output="sos")
        a_filt = signal.sosfiltfilt(sos, a_uni)
    else:
        sos = signal.butter(4, [10.0 / (fs / 2), f_high / (fs / 2)], btype="bandpass", output="sos")
        a_filt = signal.sosfiltfilt(sos, a_uni)

    # integrate a -> velocity
    velocity = np.cumsum(a_filt) * dt

    # highpass อีกรอบเพื่อตัด drift
    sos_hp = signal.butter(4, 10.0 / (fs / 2), btype="highpass", output="sos")
    velocity = signal.sosfiltfilt(sos_hp, velocity)

    v_rms_mms = float(np.sqrt(np.mean(velocity ** 2))) * 1000.0
    return v_rms_mms


def calculate_rms(times_ms, amplitudes):
    return calculate_velocity_rms(times_ms, amplitudes)


if __name__ == "__main__":
    import os
    data_dir = "./data"

    print("-" * 50)
    print("ทดสอบ: อ่านไฟล์ + คำนวณ velocity RMS")
    print("-" * 50)

    if not os.path.exists(data_dir):
        print(f"ไม่พบโฟลเดอร์ '{data_dir}'")
    else:
        for fname in sorted(f for f in os.listdir(data_dir) if f.endswith(".txt")):
            data = parse_vibration_file(os.path.join(data_dir, fname))
            if data is None:
                continue
            v = calculate_velocity_rms(data["Times_ms"], data["Amplitudes"])
            print(f"  {data['Equipment']}  |  {data['Timestamp'].date()}  |  {v:.3f} mm/s")
