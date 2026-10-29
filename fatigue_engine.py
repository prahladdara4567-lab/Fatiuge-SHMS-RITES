import pandas as pd
import numpy as np
import rainflow


def run_fatigue_analysis(excel_file, detail_category):

    FATIGUE_DATA = {
        160: {"loga3": 12.913, "loga5": 17.056, "D": 118, "L": 65},
        140: {"loga3": 12.739, "loga5": 16.768, "D": 103, "L": 57},
        125: {"loga3": 12.592, "loga5": 16.520, "D": 92, "L": 51},
        112: {"loga3": 12.449, "loga5": 16.282, "D": 83, "L": 45},
        100: {"loga3": 12.301, "loga5": 16.038, "D": 74, "L": 40},
        90: {"loga3": 12.164, "loga5": 15.807, "D": 66, "L": 36},
        80: {"loga3": 12.010, "loga5": 15.551, "D": 59, "L": 32},
        71: {"loga3": 11.855, "loga5": 15.292, "D": 52, "L": 29},
        63: {"loga3": 11.699, "loga5": 15.032, "D": 46, "L": 25},
        56: {"loga3": 11.546, "loga5": 14.777, "D": 41, "L": 23},
        50: {"loga3": 11.398, "loga5": 14.531, "D": 37, "L": 20},
        45: {"loga3": 11.261, "loga5": 14.302, "D": 33, "L": 18},
        40: {"loga3": 11.107, "loga5": 14.046, "D": 29, "L": 16},
        36: {"loga3": 10.970, "loga5": 13.817, "D": 27, "L": 15},
    }

    def cycles_to_failure(stress_range):

        if stress_range <= 0:
            return np.inf

        data = FATIGUE_DATA[detail_category]

        if stress_range < data["L"]:
            return np.inf

        if stress_range <= data["D"]:
            m = 5
            loga = data["loga5"]
        else:
            m = 3
            loga = data["loga3"]

        return (10 ** loga) / (stress_range ** m)

    # ==========================
    # READ EXCEL
    # ==========================

    df = pd.read_excel(excel_file)

    df.columns = df.columns.str.strip()

    print("Available Columns:")
    print(df.columns.tolist())

    # TIME COLUMN

    time_column = None

    for col in ["Time", "TIME", "Time_s", "Time(sec)"]:
        if col in df.columns:
            time_column = col
            break

    if time_column is None:
        raise ValueError(
            f"Time column not found. Available columns = {df.columns.tolist()}"
        )

    # STRESS COLUMN

    stress_column = None

    possible_names = [
        "Stress_MPa",
        "Stress",
        "Stress MPa",
        "Stress(MPa)",
        "Sigma"
    ]

    for col in possible_names:
        if col in df.columns:
            stress_column = col
            break

    if stress_column is None:
        raise ValueError(
            f"Stress column not found. Available columns = {df.columns.tolist()}"
        )

    time = df[time_column].to_numpy()
    stress = df[stress_column].to_numpy()

    # ==========================
    # MONITORING
    # ==========================

    monitoring_start = float(time[0])
    monitoring_end = float(time[-1])

    monitoring_seconds = monitoring_end - monitoring_start
    monitoring_hours = monitoring_seconds / 3600.0
    monitoring_days = monitoring_seconds / 86400.0

    # ==========================
    # RAINFLOW
    # ==========================

    cycles = rainflow.extract_cycles(stress)

    total_damage = 0.0

    stress_ranges = []
    cycle_counts = []

    for rng, mean, count, start, end in cycles:

        stress_range = abs(rng)

        N = cycles_to_failure(stress_range)

        damage = 0.0 if np.isinf(N) else count / N

        total_damage += damage

        stress_ranges.append(stress_range)
        cycle_counts.append(count)

    max_stress = np.max(stress)
    min_stress = np.min(stress)

    max_range = max(stress_ranges)
    total_cycles = np.sum(cycle_counts)

    # ==========================
    # ANNUAL DAMAGE
    # ==========================

    if monitoring_days > 0:
        annual_damage = total_damage * 365.0 / monitoring_days
    else:
        annual_damage = total_damage

    if annual_damage > 0:
        remaining_life_years = 1.0 / annual_damage
    else:
        remaining_life_years = np.inf

    # ==========================
    # SUMMARY TABLE
    # ==========================

    summary_df = pd.DataFrame({
        "Parameter": [
            "Detail Category",
            "Monitoring Start (s)",
            "Monitoring End (s)",
            "Monitoring Duration (s)",
            "Monitoring Hours",
            "Monitoring Days",
            "Maximum Stress (MPa)",
            "Minimum Stress (MPa)",
            "Maximum Range (MPa)",
            "Total Cycles",
            "Measured Damage",
            "Annual Damage",
            "Remaining Life (Years)"
        ],
        "Value": [
            detail_category,
            monitoring_start,
            monitoring_end,
            monitoring_seconds,
            monitoring_hours,
            monitoring_days,
            max_stress,
            min_stress,
            max_range,
            total_cycles,
            total_damage,
            annual_damage,
            remaining_life_years
        ]
    })

    return summary_df