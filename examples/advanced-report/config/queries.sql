-- Aggregate metrics by time period
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM timestamp) < 6  THEN 'Off-Peak'
        WHEN EXTRACT(HOUR FROM timestamp) < 18 THEN 'Business'
        ELSE 'Peak'
    END AS period,
    AVG(latency_ms) AS avg_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99,
    COUNT(*) AS sample_count
FROM metrics
WHERE timestamp >= NOW() - INTERVAL '14 days'
GROUP BY period
ORDER BY avg_latency DESC;

-- Storage IOPS demand vs capacity
SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(iops) AS avg_iops,
    MAX(iops) AS peak_iops
FROM storage_metrics
WHERE hostname LIKE 'db-primary-%'
GROUP BY hour
ORDER BY hour;
