import numpy as np
import pandas as pd


df = pd.read_csv("../setup/readings.csv")

print("Dataset loaded successfully.")
print("Number of rows:", len(df))
print()

def rolling_mean(values, window):
    values = np.asarray(values, dtype=float)

    result = np.zeros(len(values))

    for i in range(len(values)):
        start = max(0, i - window + 1)
        result[i] = np.mean(values[start:i + 1])

    return result


def detect_silent_drift(df, window):
    """
    Detect gradual changes using a moving-average window.

    A current window is compared with an earlier baseline window.
    """

    hr = df["hr"].values
    acc = df["acc"].values

    current_hr = rolling_mean(hr, window)

    # Earlier baseline: same-size window immediately before
    baseline_hr = np.zeros(len(df))

    for i in range(len(df)):

        current_start = max(0, i - window + 1)
        baseline_end = current_start

        baseline_start = max(0, baseline_end - window)

        if baseline_end > baseline_start:
            baseline_hr[i] = np.mean(
                hr[baseline_start:baseline_end]
            )
        else:
            baseline_hr[i] = current_hr[i]

    # Difference between current and previous window
    hr_change = np.abs(current_hr - baseline_hr)

    # ACC moving average
    current_acc = rolling_mean(acc, window)

    # Gradual HR change + relatively low acceleration
    prediction = (
        (hr_change > 2.0) &
        (current_acc < 0.12)
    ).astype(int)

    return prediction


def precision_recall_f1(y_true, y_pred):

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return precision, recall, f1


print("========== LEVEL 3 WINDOW EXPERIMENT ==========")

results = []

for window in [30, 60]:

    prediction = detect_silent_drift(df, window)

    mask = df["anomaly_type"].isin(
        ["silent_drift", "normal"]
    )

    y_true = (
        df.loc[mask, "anomaly_type"] == "silent_drift"
    ).astype(int)

    y_pred = prediction[mask.to_numpy()]

    precision, recall, f1 = precision_recall_f1(
        y_true,
        y_pred
    )

    results.append(
        (window, precision, recall, f1)
    )

    print(
        f"window={window}s | "
        f"precision={precision:.4f} | "
        f"recall={recall:.4f} | "
        f"F1={f1:.4f}"
    )


best = max(results, key=lambda x: x[3])

print()
print("========== BEST WINDOW ==========")
print(
    f"Best window: {best[0]}s"
)
print(
    f"Precision: {best[1]:.4f}"
)
print(
    f"Recall: {best[2]:.4f}"
)
print(
    f"F1: {best[3]:.4f}"
)

print()
print("========== EXPERIMENT COMPLETE ==========")