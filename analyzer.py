from dataclasses import dataclass

# threshold ตาม ISO 10816-3 (mm/s RMS)
# format: [A/B, B/C, C/D]
ISO_THRESHOLDS = {
    "group2_rigid":    [1.4, 2.8, 4.5],
    "group2_flexible": [2.3, 4.5, 7.1],
    "group1_rigid":    [2.3, 4.5, 7.1],
    "group1_flexible": [3.5, 7.1, 11.0],
}

ZONE_INFO = [
    ("Newly Commissioned",     "GOOD",     "🟢"),
    ("Unrestricted Operation", "WARNING",  "🟡"),
    ("Restricted Operation",   "ALERT",    "🟠"),
    ("Damage / Failure",       "CRITICAL", "🔴"),
]


@dataclass
class ZoneResult:
    zone: int
    label: str
    name: str
    severity: str
    color_emoji: str
    description: str
    rms: float
    thresholds: list


class ISOAnalyzer:
    def __init__(self, machinery_group="group2", foundation="rigid"):
        key = f"{machinery_group}_{foundation}"
        if key not in ISO_THRESHOLDS:
            raise ValueError(f"ไม่รู้จัก config '{key}' — ลองใช้: {list(ISO_THRESHOLDS)}")
        self.thresholds = ISO_THRESHOLDS[key]
        self.config_key = key

    def classify(self, rms_value):
        t = self.thresholds
        if rms_value <= t[0]:
            zone = 0
        elif rms_value <= t[1]:
            zone = 1
        elif rms_value <= t[2]:
            zone = 2
        else:
            zone = 3

        name, severity, emoji = ZONE_INFO[zone]
        label = chr(ord("A") + zone)
        desc = f"{emoji} [ZONE {label}] [{severity}] — {name} · {rms_value:.3f} mm/s"

        return ZoneResult(
            zone=zone, label=label, name=name,
            severity=severity, color_emoji=emoji,
            description=desc, rms=rms_value,
            thresholds=self.thresholds,
        )

    def classify_status(self, rms_value):
        return self.classify(rms_value).description

    def zone_color(self, zone):
        return ["#00c896", "#a8d400", "#ffb800", "#ff3c3c"][zone]

    @property
    def boundary_labels(self):
        t = self.thresholds
        return f"A/B={t[0]}  B/C={t[1]}  C/D={t[2]}  [{self.config_key}]"


if __name__ == "__main__":
    analyzer = ISOAnalyzer("group2", "rigid")
    print(f"Config: {analyzer.boundary_labels}\n")

    tests = [
        ("Motor Compressor OAH-06_A", 2.403),
        ("Cooling Pump OAH-02",       3.069),
        ("Jockey Pump",               6.089),
    ]
    for name, v in tests:
        r = analyzer.classify(v)
        print(f"  {name}: {v} mm/s → {r.description}")
