# RoseAmor - Prueba Técnica: Data Full Stack Engineer

Este repositorio contiene la solución a la prueba técnica para el rol de Ingeniero Full Stack de Datos. El proyecto abarca desde la ingesta y limpieza de datos, el modelado relacional, la creación de métricas clave (KPIs) y una aplicación web funcional para el registro de nuevos pedidos.

## 1. Arquitectura y Flujo de Datos
El diseño sigue una arquitectura de datos de 3 capas (Medallion Architecture adaptada):
1. **Raw (Bronze):** Los archivos CSV originales (`orders`, `customers`, `products`).
2. **Staging (Silver):** Vistas/Scripts de limpieza que corrigen inconsistencias, imputan nulos y castean tipos de datos.
3. **Consumo (Gold):** Un modelo estrella (Star Schema) compuesto por una Tabla de Hechos (`fact_orders`) y dos dimensiones (`dim_customers`, `dim_products`) conectadas al motor de BI.

## 2. Limpieza de Datos (Hallazgos y Decisiones)
Durante el análisis exploratorio (EDA) se encontraron y resolvieron las siguientes anomalías inyectadas en los datos:
* **Duplicados:** Se detectaron 15 registros duplicados en `orders.csv`. Se eliminaron usando la función correspondiente en la herramienta de BI / SQL (cláusula `DISTINCT`).
* **Valores Negativos:** Se detectaron 8 cantidades (`quantity`) negativas en órdenes y 3 costos negativos (`cost`) en productos. Se aplicó la función de valor absoluto (`ABS()`) asumiendo errores de tipografía manual.
* **Valores Nulos:** * 10 nulos en `unit_price`: Se imputaron temporalmente a 0 o se recalcularon basados en promedios históricos (dependiendo de la regla de negocio).
  * 2 nulos en `category` (Productos) y 5 nulos en `country`/`segment` (Clientes): Se imputaron como "Desconocido" o "Sin Categoría" para evitar romper la integridad referencial en el Dashboard.
* **Fechas Invalidas:** Se formatearon los campos de fecha (ej. `2025-05-28 00:00:00` en `orders`) a tipo `DATE` estándar `YYYY-MM-DD`.

## 3. Modelo de Datos
El modelo relacional está construido como un **Star Schema**:
* **`fact_orders`** (Tabla central): Contiene `order_id`, `customer_id`, `sku`, `quantity`, `unit_price`, `order_date`, `channel`.
* **`dim_customers`**: Relacionada mediante `customer_id` (1:N).
* **`dim_products`**: Relacionada mediante `sku` (1:N).

## 4. Instrucciones de Ejecución de la App Web
La aplicación es una pantalla web minimalista construida en **Python (Flask)** con **SQLite**.

### Requisitos
* Python 3.8+ instalado.

### Pasos para correr en cualquier PC
1. Clonar el repositorio.
2. Abrir una terminal en la carpeta del proyecto.
3. Instalar Flask: `pip install Flask`
4. Ejecutar la app: `python app.py`
5. Abrir el navegador en: `http://127.0.0.1:5000`

**¿Dónde queda la data?** Al correr la app por primera vez, se genera automáticamente un archivo `roseamor_orders.db` (SQLite) en la misma carpeta. Todos los nuevos pedidos se insertan en la tabla `web_orders` de esa base de datos, cumpliendo con las validaciones de campos no negativos y obligatorios.

## 5. Proceso de Actualización (Refresh)
Si mañana llega un nuevo CSV:
1. Reemplazar los archivos en la carpeta de origen.
2. Si se usa Power BI: Clic en el botón "Actualizar" del dashboard. Power Query automáticamente volverá a ejecutar todos los pasos de limpieza (remover duplicados, imputar nulos, valores absolutos) e ingestar la nueva data sin intervención manual.