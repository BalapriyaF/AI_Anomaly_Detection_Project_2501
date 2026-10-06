# AI-Driven Anomaly Detection and Monitoring System

**USN:** 1DA25SCS01  
**Seed:** 2501

## Selected questions
- Question A — Detect the abnormal readings
- Question C — Design the full system

## Run

Install:
```bash
pip install numpy pandas scikit-learn matplotlib
```

Generate/check the personal dataset:
```bash
cd setup
python generate_data.py
```

Question A:
```bash
cd ../question_A
python level1_isolation_forest.py
python level2_zscore.py
```

**Before Level 3:** commit `level3_prediction.md` to GitHub, then run:
```bash
python level3_window_experiment.py
```

Question C:
```bash
cd ../question_C
python load_data.py
```

Run the three statements in `queries.sql` using SQLite.

## Submission checklist
- New GitHub repository
- setup/generate_data.py
- setup/readings.csv
- setup/signal_plot.png
- Question A Levels 1–3
- Question C Levels 1–3
- README.md
- PERSONAL_INTELLIGENCE.md
- At least four commits
- 3–5 minute demo video
- Google Drive link with viewer access
- GitHub + Drive links emailed to the assignment address
