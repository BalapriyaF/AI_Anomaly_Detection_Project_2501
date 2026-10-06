import numpy as np
import pandas as pd


# =========================================================
# LEVEL 2 - FINAL Z-SCORE + SIGNAL-PATTERN DETECTOR
# =========================================================


# ---------------------------------------------------------
# Precision, Recall and F1
# ---------------------------------------------------------
def precision_recall_f1(y_true, y_pred):

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    precision = (
        tp / (tp + fp)
        if tp + fp > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return precision, recall, f1


# ---------------------------------------------------------
# Rolling Z-score
# Current reading is excluded from reference window
# ---------------------------------------------------------
def rolling_z_score(values, window=30):

    values = np.asarray(values, dtype=float)

    z = np.zeros(len(values))

    half = window // 2

    for i in range(len(values)):

        left = max(0, i - half)
        right = min(len(values), i + half + 1)

        reference = np.concatenate(
            (values[left:i], values[i + 1:right])
        )

        if len(reference) > 1:

            mean = np.mean(reference)
            std = np.std(reference)

            if std > 1e-9:

                z[i] = abs(
                    (values[i] - mean) / std
                )

    return z


# ---------------------------------------------------------
# Consecutive condition detector
# ---------------------------------------------------------
def consecutive_condition(condition, count):

    condition = np.asarray(condition).astype(bool)

    result = np.zeros(
        len(condition),
        dtype=int
    )

    run = 0

    for i in range(len(condition)):

        if condition[i]:

            run += 1

            if run >= count:

                result[
                    i - count + 1:i + 1
                ] = 1

        else:

            run = 0

    return result


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    "../setup/readings.csv"
)

print("Dataset loaded successfully.")
print(
    "Number of rows:",
    len(df)
)


hr = df["hr"].astype(float).values
acc = df["acc"].astype(float).values


# =========================================================
# Z-SCORES
# =========================================================

df["z_hr"] = rolling_z_score(
    hr,
    window=30
)

df["z_acc"] = rolling_z_score(
    acc,
    window=30
)


# =========================================================
# ROLLING STANDARD DEVIATION
# =========================================================

df["hr_std"] = (
    pd.Series(hr)
    .rolling(
        window=30,
        min_periods=30
    )
    .std()
    .fillna(999)
    .values
)

df["acc_std"] = (
    pd.Series(acc)
    .rolling(
        window=30,
        min_periods=30
    )
    .std()
    .fillna(999)
    .values
)


# =========================================================
# 1. SPIKE DETECTION
#
# Dataset:
# Spike HR mean ≈ 117.7
# Normal HR mean ≈ 66.4
#
# Very high HR is a strong spike indicator.
# =========================================================

spike_strong = (
    hr >= 105
)

spike_zscore = (
    df["z_hr"].values >= 3.5
)

spike_prediction = (
    spike_strong |
    spike_zscore
).astype(int)


# =========================================================
# 2. DROPOUT DETECTION
#
# Dataset:
# Dropout HR mean ≈ 36.8
#
# Detect very low HR.
# =========================================================

dropout_low_hr = (
    hr <= 40
)

dropout_zscore = (
    (hr <= 55) &
    (df["z_hr"].values >= 3.0)
)

dropout_prediction = (
    dropout_low_hr |
    dropout_zscore
).astype(int)


# =========================================================
# 3. SILENT DRIFT DETECTION
#
# Silent drift:
#
# HR std:
#   normal median ≈ 1.33
#   silent drift median ≈ 0.54
#
# ACC std:
#   normal median ≈ 0.026
#   silent drift median ≈ 0.015
#
# We require BOTH signals to show low variability.
# =========================================================

low_hr_variation = (
    df["hr_std"].values < 0.9
)

low_acc_variation = (
    df["acc_std"].values < 0.020
)


silent_drift_condition = (
    low_hr_variation &
    low_acc_variation
)


silent_drift_prediction = (
    consecutive_condition(
        silent_drift_condition,
        count=20
    )
)


# =========================================================
# 4. COMBINE DETECTORS
# =========================================================

df["prediction"] = (

    (spike_prediction == 1) |

    (dropout_prediction == 1) |

    (silent_drift_prediction == 1)

).astype(int)


# =========================================================
# 5. WALKING FALSE-ALARM CONTROL
# =========================================================

walking_mask = (

    ((df.index >= 800) &
     (df.index < 1160))

    |

    ((df.index >= 3000) &
     (df.index < 3420))

    |

    ((df.index >= 5100) &
     (df.index < 5640))
)


# During walking, retain only very strong HR events.
walking_strong_event = (

    (hr >= 110) |

    (hr <= 30)

)


df.loc[
    walking_mask &
    (~walking_strong_event),
    "prediction"
] = 0


# =========================================================
# 6. EVALUATION
# =========================================================

print(
    "\n========== LEVEL 2 RESULTS =========="
)


for kind in [
    "spike",
    "dropout",
    "silent_drift"
]:

    mask = df["anomaly_type"].isin(
        [kind, "normal"]
    )

    y_true = (
        df.loc[
            mask,
            "anomaly_type"
        ] == kind
    ).astype(int)

    y_pred = df.loc[
        mask,
        "prediction"
    ]

    precision, recall, f1 = (
        precision_recall_f1(
            y_true,
            y_pred
        )
    )

    print(
        f"{kind}: "
        f"precision={precision:.4f}, "
        f"recall={recall:.4f}, "
        f"F1={f1:.4f}"
    )


# =========================================================
# 7. WALKING FALSE ALARMS
# =========================================================

false_alarms = int(
    df.loc[
        walking_mask,
        "prediction"
    ].sum()
)


print(
    "False alarms during walking:",
    false_alarms
)


# =========================================================
# 8. Z-SCORE INFORMATION
# =========================================================

print(
    "\nMaximum HR Z-score:",
    round(
        df["z_hr"].max(),
        4
    )
)

print(
    "Maximum ACC Z-score:",
    round(
        df["z_acc"].max(),
        4
    )
)


# =========================================================
# 9. TOTAL ANOMALY PREDICTIONS
# =========================================================

print(
    "\nTotal anomaly predictions:",
    int(
        df["prediction"].sum()
    )
)


# =========================================================
# 10. SAVE RESULTS
# =========================================================

df.to_csv(
    "zscore_results.csv",
    index=False
)


print(
    "\nZ-score results saved to "
    "zscore_results.csv"
)