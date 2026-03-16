class ISOAnalyzer:
    def __init__(self):
        # ISO 10816-3 Thresholds
        self.yellow_limit = 2.3
        self.orange_limit = 4.5
        self.red_limit = 7.1

    def classify_status(self, rms_value):
        """Classifies machine status based on ISO standards with custom English tags."""
        if rms_value <= self.yellow_limit:
            return "🟢 [NORMAL] Zone A - Machine is operating normally"
        elif rms_value <= self.orange_limit:
            return "🟡 [WARNING] Zone B - Acceptable for unrestricted long-term operation"
        elif rms_value <= self.red_limit:
            return "🟠 [ALERT] Zone C - Unsatisfactory for long-term operation (Monitor closely)"
        else:
            return "🔴 [CRITICAL] Zone D - Vibration causes damage (Immediate action required)"

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