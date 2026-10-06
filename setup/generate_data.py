import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 2501
N = 7200
rng = np.random.default_rng(SEED)
t = np.arange(N)

resting_hr = 60 + (SEED % 20)

hr = (
    resting_hr
    + 2.0*np.sin(2*np.pi*t/3600)
    + 0.9*(t/N)
    + 1.0*np.sin(2*np.pi*t/8)
    + rng.normal(0,1.1,N)
)
acc = np.abs(rng.normal(0.08,0.025,N))

walking_periods = [(800,360),(3000,420),(5100,540)]
for start,duration in walking_periods:
    p=np.arange(duration)
    acc[start:start+duration] = (
        0.75 + 0.16*np.abs(np.sin(2*np.pi*p/1.8))
        + rng.normal(0,0.045,duration)
    )
    hr[start:start+duration] += 25 + 2*np.sin(2*np.pi*p/duration)

label=np.zeros(N,dtype=int)
anomaly_type=np.full(N,"normal",dtype=object)

events=[
    (150,"spike"),(650,"dropout"),(1200,"silent_drift"),
    (1750,"spike"),(2250,"dropout"),(2600,"silent_drift"),
    (2900,"spike"),(3650,"dropout"),(4000,"silent_drift"),
    (4350,"spike"),(4700,"dropout"),(5050,"silent_drift"),
    (5700,"spike"),(6050,"dropout"),(6300,"silent_drift"),
    (6550,"spike"),(6750,"dropout"),(6950,"silent_drift"),
    (7100,"spike"),(7160,"dropout")
]

for i,(start,kind) in enumerate(events):
    if kind=="spike":
        duration=int(rng.integers(3,11))
        hr[start:start+duration]+=float(rng.uniform(45,60))
    elif kind=="dropout":
        duration=int(rng.integers(10,31))
        if i%2==0:
            hr[start:start+duration]=0
        else:
            hr[start:start+duration]=hr[start-1]
    else:
        # Keep the 5-minute drift fully inside the 7200-row dataset.
        duration=min(300,N-start)
        start_hr=hr[start]
        hr[start:start+duration]=(
            start_hr + np.linspace(0,15,duration)
            + rng.normal(0,0.30,duration)
        )
        acc[start:start+duration]=np.abs(
            rng.normal(0.05,0.015,duration)
        )
    label[start:start+duration]=1
    anomaly_type[start:start+duration]=kind

readings=pd.DataFrame({
    "timestamp":pd.date_range("2026-10-06 00:00:00",periods=N,freq="s"),
    "hr":np.round(hr,3),
    "acc":np.round(acc,4),
    "label":label,
    "anomaly_type":anomaly_type
})
readings.to_csv("readings.csv",index=False)

plt.figure(figsize=(15,5))
plt.plot(readings.timestamp,readings.hr,linewidth=.7,label="Heart rate")
m=readings.label.eq(1)
plt.scatter(readings.loc[m,"timestamp"],readings.loc[m,"hr"],s=5,label="Labelled anomaly")
plt.xlabel("Timestamp"); plt.ylabel("Heart rate (bpm)")
plt.title("Wearable Heart Rate Signal — Personal Seed 2501")
plt.legend(); plt.tight_layout()
plt.savefig("signal_plot.png",dpi=180); plt.close()
