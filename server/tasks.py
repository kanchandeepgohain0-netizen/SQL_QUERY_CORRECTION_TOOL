from typing import List, Tuple

# =========================
# TASK 1 — SYNTAX ERROR
# =========================
task_1 = {
    "id": "task_1_syntax",
    "description": "Fix SQL syntax to return names of users older than 18.",
    "broken_query": "SELCT name FORM users WHER age > 18",
    "expected_query": "SELECT name FROM users WHERE age > 18",
}

# =========================
# TASK 2 — LOGIC ERROR (JOIN)
# =========================
task_2 = {
    "id": "task_2_logic",
    "description": "Fix the JOIN condition to correctly match customers with their orders.",
    "broken_query": """
SELECT customers.name, orders.amount
FROM orders
JOIN customers ON orders.id = customers.id
""",
    "expected_query": """
SELECT customers.name, orders.amount
FROM orders
JOIN customers ON orders.customer_id = customers.id
""",
}

# =========================
# TASK 3 — OPTIMIZATION
# =========================
task_3 = {
    "id": "task_3_optimization",
    "description": "Fix correlated subquery and aggregation. Return products with total quantity > 10 using efficient JOIN.",
    "broken_query": """
SELECT p.name,
(SELECT SUM(qty) FROM order_items WHERE product_id = p.id) AS total
FROM products p
WHERE total > 10
""",
    "expected_query": """
SELECT p.name, SUM(oi.qty) AS total
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id, p.name
HAVING SUM(oi.qty) > 10
""",
}

def columns_match(result_columns: List[str], expected_columns: List[str]) -> bool:
    return result_columns == expected_columns

def row_overlap_ratio(result_rows: List[Tuple], expected_rows: List[Tuple]) -> float:
    # Convert to sets for deterministic comparison
    result_set = set(result_rows)
    expected_set = set(expected_rows)

    if len(expected_set) == 0:
        return 0.0

    overlap = len(result_set & expected_set)
    return overlap / len(expected_set)

def compute_reward(
    has_error: bool,
    result_columns: List[str],
    expected_columns: List[str],
    result_rows: List[Tuple],
    expected_rows: List[Tuple],
) -> float:

    # 1. Syntax error
    if has_error:
        return 0.0

    # 2. Empty result
    if len(result_rows) == 0:
        return 0.1

    # 3. Column mismatch
    if not columns_match(result_columns, expected_columns):
        return 0.2

    # 4. Row comparison
    ratio = row_overlap_ratio(result_rows, expected_rows)

    # 5. Scoring based on ratio
    # Exact match (both directions)
    if ratio == 1.0 and len(result_rows) == len(expected_rows):
        return 1.0
    elif ratio >= 0.5:
        return 0.7
    elif 0.3 <= ratio < 0.5:
        return 0.5
    else:
        return 0.35
    
# =========================
# TASK REGISTRY
# =========================
TASKS = {
    "task_1_syntax": task_1,
    "task_2_logic": task_2,
    "task_3_optimization": task_3,
}