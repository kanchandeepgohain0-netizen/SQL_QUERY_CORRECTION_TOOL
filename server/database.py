import sqlite3
import os

def create_database(task_id: str):
    db_path = f"{task_id}.db"

    # Remove existing DB to ensure clean reset
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    return conn, cursor

def setup_task_1(conn, cursor):
    # Create table
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        email TEXT
    )
    """)

    # Insert sample data
    users_data = [
        (1, "Alice", 25, "alice@example.com"),
        (2, "Bob", 17, "bob@example.com"),
        (3, "Charlie", 30, "charlie@example.com"),
        (4, "David", 15, "david@example.com"),
        (5, "Eve", 22, "eve@example.com")
    ]

    cursor.executemany(
        "INSERT INTO users (id, name, age, email) VALUES (?, ?, ?, ?)",
        users_data
    )

    conn.commit()

def setup_task_2(conn, cursor):
    # Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    # Create orders table
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL
    )
    """)

    # Insert customers
    customers_data = [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ]

    cursor.executemany(
        "INSERT INTO customers (id, name) VALUES (?, ?)",
        customers_data
    )

    # Insert orders
    orders_data = [
        (1, 1, 100.0),
        (2, 2, 200.0),
        (3, 1, 150.0),
        (4, 3, 300.0)
    ]

    cursor.executemany(
        "INSERT INTO orders (id, customer_id, amount) VALUES (?, ?, ?)",
        orders_data
    )

    conn.commit()

def setup_task_3(conn, cursor):
    # Create categories table
    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    # Create products table
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category_id INTEGER,
        price REAL
    )
    """)

    # Create order_items table
    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        qty INTEGER
    )
    """)

    # Insert categories
    categories_data = [
        (1, "Electronics"),
        (2, "Clothing")
    ]

    cursor.executemany(
        "INSERT INTO categories (id, name) VALUES (?, ?)",
        categories_data
    )

    # Insert products
    products_data = [
        (1, "Laptop", 1, 1000.0),
        (2, "Phone", 1, 500.0),
        (3, "Shirt", 2, 50.0)
    ]

    cursor.executemany(
        "INSERT INTO products (id, name, category_id, price) VALUES (?, ?, ?, ?)",
        products_data
    )

    # Insert order_items
    order_items_data = [
        (1, 1, 1, 5),   # Laptop qty 5
        (2, 1, 2, 3),   # Phone qty 3
        (3, 2, 1, 6),   # Laptop qty 6 → total 11 (>10)
        (4, 2, 3, 2),   # Shirt qty 2
        (5, 3, 2, 4)    # Phone qty total = 7
    ]

    cursor.executemany(
        "INSERT INTO order_items (id, order_id, product_id, qty) VALUES (?, ?, ?, ?)",
        order_items_data
    )

    conn.commit()