import sympy as sp
from sympy import symbols, solve, factor, expand, simplify, limit, diff, integrate

tool_definition = {
    "name": "sympy",
    "description": (
        "### Instructions:\n"
        "Use this tool to perform symbolic mathematical operations using the SymPy library. "
        "This includes algebraic simplification, equation solving, limits, derivatives, integrals, and more. "
        "It's suitable for performing exact, symbolic computation (not numerical approximation).\n\n"
        "Always specify the `operation` and a valid `expression`. "
        "Use `variables` to indicate which variables to differentiate, integrate, or solve for.\n"
        "Use `assumptions` if needed to guide symbolic behavior (e.g., assume variable is `positive`, `real`, or `integer`).\n"
        "Use `point` only when computing limits.\n\n"
        "### Supported Operations:\n"
        "- `solve`: Solve algebraic equations.\n"
        "- `factor`: Factor an expression.\n"
        "- `expand`: Expand expressions (e.g., multiply out polynomials).\n"
        "- `simplify`: Simplify expressions.\n"
        "- `limit`: Compute the limit of an expression as a variable approaches a point.\n"
        "- `differentiate`: Compute the derivative with respect to a variable.\n"
        "- `integrate`: Compute the indefinite integral.\n"
        "- `series`: Compute a Taylor series expansion at 0 up to the 4th order.\n"
        "- `matrix`: Compute determinant, inverse, and eigenvalues of a symbolic matrix (input must be a 2D list).\n\n"
        "### Example Expression Formats:\n"
        "- `x**2 + 2*x + 1`\n"
        "- `sin(x)/x`\n"
        "- `diff(x**2, x)` (if using operation `differentiate`)\n"
        "- `[[1, 2], [3, 4]]` (if using operation `matrix`)\n"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "The symbolic operation to perform (e.g., solve, simplify, integrate, etc.)",
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
                "description": "The mathematical expression to evaluate, written as a Python string.",
            },
            "variables": {
                "type": "string",
                "description": "Comma-separated list of variables to operate on (default is 'x').",
                "default": "x",
            },
            "assumptions": {
                "type": "string",
                "description": "Optional variable assumptions (e.g., 'positive,real') to refine the symbolic behavior.",
                "default": "",
            },
            "point": {
                "type": "string",
                "description": "Point to evaluate limit at (e.g., '0', 'oo', '-oo'). Only used with the 'limit' operation.",
                "default": "",
            },
        },
        "required": ["operation", "expression"],
    },
}


def handle_call(input_data):
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
