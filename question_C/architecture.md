# Question C — Level 1 Architecture

```text
Wearable Device
      |
      v
Ingestion API / Message Queue
      |
      +-------------------+
      |                   |
      v                   v
Raw Readings DB      Detection Service
      |                   |
      |                   v
      |              Alerts Table
      |                   |
      v                   v
Dashboard <--------- Alert Service
                          |
                          v
                   User Notification
```

The system contains device, ingestion, database, detection, dashboard and alerting layers.
