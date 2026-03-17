class ISOAnalyzer:
    def __init__(self):
        self.yellow_limit = 2.3
        self.orange_limit = 4.5
        self.red_limit = 7.1

    def classify_status(self, rms_value):
        """Classifies status with clear English descriptions for reports."""
        if rms_value <= self.yellow_limit:
            return "🟢 [NORMAL] - Healthy condition"
        elif rms_value <= self.orange_limit:
            return "🟡 [WARNING] - Minor vibration detected"
        elif rms_value <= self.red_limit:
            return "🟠 [ALERT] - Significant vibration (Action required)"
        else:
            return "🔴 [CRITICAL] - Machine failure / Damage likely"

if __name__ == "__main__":
    print("-" * 50)
    print("Step 2 Test: ISO 10816-3 Status Analysis")
    print("-" * 50)
    test_rms_value = 0.2792
    analyzer = ISOAnalyzer()
    status = analyzer.classify_status(test_rms_value)
    print(f"📌 Equipment: Motor Compressor OAH-06_A")
    print(f"📈 Vibration RMS: {test_rms_value:.4f}")
    print(f"📊 Evaluation: {status}")
