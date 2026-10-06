import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_fscore_support

SEED=2501
df=pd.read_csv("../setup/readings.csv")
w=30
df["hr_mean"]=df.hr.rolling(w,center=True,min_periods=1).mean()
df["hr_std"]=df.hr.rolling(w,center=True,min_periods=1).std().fillna(0)
df["hr_slope"]=df.hr.diff().fillna(0)
df["acc_mean"]=df.acc.rolling(w,center=True,min_periods=1).mean()
features=["hr","acc","hr_mean","hr_std","hr_slope","acc_mean"]

model=IsolationForest(n_estimators=200,contamination=0.04,random_state=SEED)
model.fit(df[features])
df["anomaly_score"]=-model.decision_function(df[features])
df["prediction"]=(model.predict(df[features])==-1).astype(int)

for kind in ["spike","dropout","silent_drift"]:
    mask=df.anomaly_type.isin([kind,"normal"])
    y_true=(df.loc[mask,"anomaly_type"]==kind).astype(int)
    y_pred=df.loc[mask,"prediction"]
    p,r,f1,_=precision_recall_fscore_support(y_true,y_pred,average="binary",zero_division=0)
    print(f"{kind}: precision={p:.4f}, recall={r:.4f}, F1={f1:.4f}")

walking_mask=((df.index>=800)&(df.index<1160))|((df.index>=3000)&(df.index<3420))|((df.index>=5100)&(df.index<5640))
print("False alarms during walking:",int(df.loc[walking_mask,"prediction"].sum()))
df.to_csv("isolation_forest_results.csv",index=False)
