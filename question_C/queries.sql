-- 1. Alerts per user in the last 24 hours
SELECT user_id, COUNT(*) AS alert_count
FROM alerts
WHERE timestamp >= datetime('now','-24 hours')
GROUP BY user_id
ORDER BY user_id;

-- 2. Users with more than five alerts in any one hour
SELECT user_id,
       strftime('%Y-%m-%d %H:00:00',timestamp) AS hour,
       COUNT(*) AS alert_count
FROM alerts
GROUP BY user_id, hour
HAVING COUNT(*) > 5
ORDER BY user_id, hour;

-- 3. Average heart rate per user per hour
SELECT user_id,
       strftime('%Y-%m-%d %H:00:00',timestamp) AS hour,
       ROUND(AVG(hr),2) AS average_heart_rate
FROM readings
GROUP BY user_id, hour
ORDER BY user_id, hour;
