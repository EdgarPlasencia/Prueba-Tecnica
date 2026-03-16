-- =======================================================
-- 1. BASE LIMPIA Y MODELO ESTRELLA VIRTUAL (CTEs)
-- =======================================================
WITH clean_orders AS (
    SELECT DISTINCT -- Elimina los 15 duplicados
        order_id,
        customer_id,
        sku,
        ABS(quantity) AS quantity, -- Corrige 8 cantidades negativas
        COALESCE(unit_price, 0) AS unit_price, -- Manejo de 10 precios nulos
        CAST(order_date AS DATE) AS order_date,
        channel
    FROM raw_orders
),
clean_products AS (
    SELECT 
        sku,
        COALESCE(category, 'Sin Categoría') AS category,
        ABS(cost) AS cost, -- Corrige 3 costos negativos
        active
    FROM raw_products
),
clean_customers AS (
    SELECT 
        customer_id,
        name,
        COALESCE(country, 'Desconocido') AS country,
        COALESCE(segment, 'Desconocido') AS segment
    FROM raw_customers
),
fact_table AS (
    -- Unimos todo para calcular ingresos y márgenes
    SELECT 
        o.order_id,
        o.customer_id,
        c.name AS customer_name,
        o.sku,
        p.category,
        o.quantity,
        o.unit_price,
        p.cost,
        (o.quantity * o.unit_price) AS total_revenue,
        (o.quantity * o.unit_price) - (o.quantity * p.cost) AS total_margin,
        o.order_date,
        STRFTIME('%Y-%m', o.order_date) AS order_month, -- O TO_CHAR() en Postgres
        o.channel
    FROM clean_orders o
    LEFT JOIN clean_products p ON o.sku = p.sku
    LEFT JOIN clean_customers c ON o.customer_id = c.customer_id
)

-- =======================================================
-- 2. RESOLUCIÓN DE KPIs Y VISUALIZACIONES (Dashboard)
-- =======================================================

-- KPI 1-4: Tarjetas Principales
SELECT 
    SUM(total_revenue) AS Ventas_Totales,
    SUM(total_margin) AS Margen_Total,
    COUNT(DISTINCT order_id) AS Numero_de_Pedidos,
    SUM(total_revenue) / COUNT(DISTINCT order_id) AS Ticket_Promedio
FROM fact_table;

-- Vis 1: Ventas por Mes
SELECT order_month, SUM(total_revenue) AS Ventas
FROM fact_table
GROUP BY order_month
ORDER BY order_month;

-- Vis 2: Ventas por Canal
SELECT channel, SUM(total_revenue) AS Ventas
FROM fact_table
GROUP BY channel
ORDER BY Ventas DESC;

-- Vis 3: Margen por Categoría
SELECT category, SUM(total_margin) AS Margen
FROM fact_table
GROUP BY category
ORDER BY Margen DESC;

-- Vis 4: Top 10 Clientes por Ingresos
SELECT customer_name, SUM(total_revenue) AS Ingresos
FROM fact_table
GROUP BY customer_name
ORDER BY Ingresos DESC
LIMIT 10;

-- Vis 5: Top 10 Productos más vendidos (por volumen)
SELECT sku, SUM(quantity) AS Unidades_Vendidas
FROM fact_table
GROUP BY sku
ORDER BY Unidades_Vendidas DESC
LIMIT 10;