from graph.agent import build_agent

result = build_agent().invoke({
    "user_query": "show me all orders with discount applied",
    "relevant_tables": None,
    "generated_sql": None,
    "is_valid": None,
    "validation_error": None,
    "query_result": None,
    "error": None,
    "db_type": None,
    "trace": None
})

print("Generated SQL:", result.get("generated_sql"))
print("Is valid:", result.get("is_valid"))
print("Validation error:", result.get("validation_error"))
print("Error:", result.get("error"))