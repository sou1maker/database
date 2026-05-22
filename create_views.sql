CREATE OR REPLACE VIEW vw_pickup_point_analytics AS
SELECT 
    pp.point_name,
    pp.capacity AS max_capacity,
    pp.current_packages,
    ROUND(pp.current_packages / pp.capacity * 100, 1) AS saturation_pct,
    (SELECT COUNT(*) FROM orders o WHERE o.pickup_point_id = pp.point_id AND o.order_status = 'Arrived_At_Point') AS backlog_count
FROM pickup_points pp
ORDER BY saturation_pct DESC;

CREATE OR REPLACE VIEW vw_merchant_sales_rank AS
SELECT 
    m.merchant_name,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_sales,
    RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS sales_rank
FROM merchants m
LEFT JOIN orders o ON m.merchant_id = o.merchant_id AND o.order_status = 'Completed'
GROUP BY m.merchant_id, m.merchant_name
ORDER BY sales_rank;
