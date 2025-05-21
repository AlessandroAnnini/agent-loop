import sympy as sp
from sympy import symbols, solve, factor, expand, simplify, limit, diff, integrate

tool_definition = {
    "name": "sympy",
    "description": "Perform symbolic mathematics operations using SymPy",
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "Mathematical operation to perform",
                "enum": [
                    "solve",
                    "factor",
                    "expand",
                    "simplify",
                    "limit",
                    "differentiate",
                    "integrate",
                    "series",
                    "matrix",
                ],
            },
            "expression": {
                "type": "string",
                "description": "Mathematical expression as a string",
            },
            "variables": {
                "type": "string",
                "description": "Variables to solve for or with respect to (comma-separated)",
                "default": "x",
            },
            "assumptions": {
                "type": "string",
                "description": "Additional assumptions like domains (e.g., 'positive,real')",
                "default": "",
            },
            "point": {
                "type": "string",
                "description": "Point for limit calculation (e.g., '0' or 'oo')",
                "default": "",
            },
        },
        "required": ["operation", "expression"],
    },
}


def handle_tool_call(input_data):
    operation = input_data["operation"]
    expr_str = input_data["expression"]
    var_str = input_data.get("variables", "x")
    assumptions_str = input_data.get("assumptions", "")
    point_str = input_data.get("point", "")

    try:
        # Parse variables
        var_list = [s.strip() for s in var_str.split(",")]
        var_symbols = {}

        # Apply assumptions if provided
        assumptions = {}
        if assumptions_str:
            assumption_list = [a.strip() for a in assumptions_str.split(",")]
            for a in assumption_list:
                if a == "positive":
                    assumptions["positive"] = True
                elif a == "real":
                    assumptions["real"] = True
                elif a == "integer":
                    assumptions["integer"] = True

        # Create symbols with assumptions
        for v in var_list:
            var_symbols[v] = symbols(v, **assumptions)

        # Get main variable for operations like diff and integrate
        main_var = var_symbols.get(var_list[0], symbols("x"))

        # Parse expression with variables
        expr = sp.sympify(expr_str, locals=var_symbols)

        # Perform the requested operation
        if operation == "solve":
            result = solve(expr, main_var)
            return f"Solutions: {result}"

        elif operation == "factor":
            result = factor(expr)
            return f"Factorized: {result}"

        elif operation == "expand":
            result = expand(expr)
            return f"Expanded: {result}"

        elif operation == "simplify":
            result = simplify(expr)
            return f"Simplified: {result}"

        elif operation == "limit":
            # Parse point value
            if point_str == "oo" or point_str == "infinity":
                point = sp.oo
            elif point_str == "-oo" or point_str == "-infinity":
                point = -sp.oo
            else:
                point = float(point_str) if point_str else 0

            result = limit(expr, main_var, point)
            return f"Limit as {main_var} → {point}: {result}"

        elif operation == "differentiate":
            result = diff(expr, main_var)
            return f"Derivative with respect to {main_var}: {result}"

        elif operation == "integrate":
            result = integrate(expr, main_var)
            return f"Indefinite integral with respect to {main_var}: {result}"

        elif operation == "series":
            result = expr.series(main_var, n=5)
            return f"Series expansion around {main_var}=0: {result}"

        elif operation == "matrix":
            # Special case for matrix operations
            # For matrices, the expression should be in the form "[[a,b],[c,d]]"
            try:
                matrix = sp.Matrix(eval(expr_str))
                det = matrix.det()
                inv = matrix.inv() if det != 0 else "Singular matrix (no inverse)"
                eigenvals = matrix.eigenvals()

                return (
                    f"Matrix:\n{matrix}\n"
                    f"Determinant: {det}\n"
                    f"Inverse:\n{inv}\n"
                    f"Eigenvalues: {eigenvals}"
                )
            except:
                return "Invalid matrix format. Use [[a,b],[c,d]] syntax."

        else:
            return f"Unsupported operation: {operation}"

    except Exception as e:
        return f"Error performing symbolic math operation: {e}"
