from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuración de SQLite
DB_NAME = "roseamor_orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            channel TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# HTML Template con Tailwind CSS para un diseño elegante
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>RoseAmor - Registro de Pedidos</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-gray-800 text-center">🛒 Nuevo Pedido - RoseAmor</h2>
        
        {% if message %}
            <div class="mb-4 p-3 rounded {{ 'bg-green-100 text-green-700' if success else 'bg-red-100 text-red-700' }}">
                {{ message }}
            </div>
        {% endif %}

        <form method="POST" action="/add_order">
            <div class="grid grid-cols-2 gap-4">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Order ID</label>
                    <input type="text" name="order_id" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Customer ID</label>
                    <input type="text" name="customer_id" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">SKU</label>
                <input type="text" name="sku" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Cantidad</label>
                    <input type="number" name="quantity" min="1" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Precio Unitario</label>
                    <input type="number" step="0.01" min="0.01" name="unit_price" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
            </div>

            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Fecha del Pedido</label>
                <input type="date" name="order_date" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>

            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2">Canal</label>
                <select name="channel" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="ecommerce">E-commerce</option>
                    <option value="wholesale">Wholesale</option>
                    <option value="retail">Retail</option>
                    <option value="export">Export</option>
                </select>
            </div>

            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full focus:outline-none focus:shadow-outline transition duration-150">
                Registrar Pedido
            </button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/add_order", methods=["POST"])
def add_order():
    try:
        # Extraer datos
        order_id = request.form['order_id']
        customer_id = request.form['customer_id']
        sku = request.form['sku']
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        order_date = request.form['order_date']
        channel = request.form['channel']

        # Validaciones (Back-end por seguridad extra)
        if quantity <= 0 or unit_price <= 0:
            return render_template_string(HTML_TEMPLATE, message="Error: Cantidad y Precio deben ser mayores a 0.", success=False)
        
        datetime.strptime(order_date, '%Y-%m-%d') # Valida formato de fecha

        # Insertar en BD
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO web_orders (order_id, customer_id, sku, quantity, unit_price, order_date, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, customer_id, sku, quantity, unit_price, order_date, channel))
        conn.commit()
        conn.close()

        return render_template_string(HTML_TEMPLATE, message=f"Pedido {order_id} guardado exitosamente.", success=True)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, message=f"Error al procesar: {str(e)}", success=False)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)