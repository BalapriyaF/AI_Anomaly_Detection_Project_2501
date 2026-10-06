# Question C — Level 3

## 1. Rows per day

1 reading/second/user × 86,400 seconds/day = 86,400 readings/day/user.

For 1,000 users:

**86,400,000 rows/day**

## 2. Writes per second

1 × 1,000 = **1,000 writes/second**

## 3. Storage per month

Using an explicit planning assumption of 100 bytes per stored reading:

86,400,000 × 100 bytes ≈ 8.64 GB/day.

For 30 days:

**≈259.2 GB/month**

This excludes indexes, metadata and replication, so actual storage is higher.

## 4. At 100,000 users

- **100,000 writes/second**
- **8.64 billion rows/day**

The first major bottleneck is likely a single database's ingestion/storage path.

## 5. Changes

Use a durable ingestion/stream layer, batch writes, partition by time/user,
horizontally scale detection workers, and use scalable time-series/distributed
storage. Keep recent raw data hot and aggregate older data.
