import ast


def analyze_python_code(code):
    """
    Analyze Python source code and generate
    basic bug, quality, security and health scores.
    """

    quality_score = 100
    security_score = 100
    bug_risk = "Low"

    review_messages = []
    refactoring_messages = []
    learning_messages = []

    # -----------------------------------
    # 1. Check whether Python syntax is valid
    # -----------------------------------

    try:
        tree = ast.parse(code)

    except SyntaxError as error:

        return {
            "bug_risk": "High",
            "quality_score": 30,
            "security_score": 50,
            "health_score": 40,
        }


    # -----------------------------------
    # 2. Count lines of code
    # -----------------------------------

    lines = code.splitlines()

    total_lines = len(lines)

    if total_lines > 300:
        quality_score -= 15
        refactoring_messages.append(
            "The file is large. Consider splitting it into smaller modules."
        )

    elif total_lines > 150:
        quality_score -= 8


    # -----------------------------------
    # 3. Detect dangerous functions
    # -----------------------------------

    dangerous_functions = [
        "eval",
        "exec",
    ]

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in dangerous_functions:

                    security_score -= 30

                    review_messages.append(
                        f"Potential security risk detected: {node.func.id}()"
                    )


    # -----------------------------------
    # 4. Detect hard-coded passwords
    # -----------------------------------

    sensitive_names = [
        "password",
        "passwd",
        "secret",
        "api_key",
        "apikey",
        "token",
    ]

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    variable_name = target.id.lower()

                    if variable_name in sensitive_names:

                        security_score -= 20

                        review_messages.append(
                            f"Possible hard-coded sensitive value: {target.id}"
                        )


    # -----------------------------------
    # 5. Detect print statements
    # -----------------------------------

    print_count = 0

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id == "print":

                    print_count += 1


    if print_count > 5:

        quality_score -= 10

        refactoring_messages.append(
            "Consider replacing excessive print statements with proper logging."
        )


    # -----------------------------------
    # 6. Detect very long functions
    # -----------------------------------

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            function_lines = (
                node.end_lineno - node.lineno
                if hasattr(node, "end_lineno")
                else 0
            )

            if function_lines > 50:

                quality_score -= 10

                refactoring_messages.append(
                    f"Function '{node.name}' is very long. "
                    "Consider breaking it into smaller functions."
                )


    # -----------------------------------
    # 7. Detect TODO / FIXME
    # -----------------------------------

    if "TODO" in code or "FIXME" in code:

        quality_score -= 5

        review_messages.append(
            "TODO/FIXME comments were found in the source code."
        )


    # -----------------------------------
    # 8. Determine Bug Risk
    # -----------------------------------

    if quality_score < 60:

        bug_risk = "High"

    elif quality_score < 80:

        bug_risk = "Medium"

    else:

        bug_risk = "Low"


    # -----------------------------------
    # 9. Generate AI-style review
    # -----------------------------------

    if not review_messages:

        review_messages.append(
            "No major issues were detected during the initial code review."
        )


    # -----------------------------------
    # 10. Learning suggestions
    # -----------------------------------

    learning_messages.append(
        "Practice writing small, reusable functions."
    )

    if security_score < 80:

        learning_messages.append(
            "Learn secure handling of passwords, tokens and sensitive information."
        )

    if quality_score < 80:

        learning_messages.append(
            "Focus on code readability, modularity and maintainability."
        )


    # -----------------------------------
    # 11. Calculate Project Health
    # -----------------------------------

    health_score = (
        quality_score +
        security_score
    ) // 2


    # Keep scores between 0 and 100

    quality_score = max(0, min(100, quality_score))

    security_score = max(0, min(100, security_score))

    health_score = max(0, min(100, health_score))


    return {

        "bug_risk": bug_risk,

        "quality_score": quality_score,

        "security_score": security_score,

        "health_score": health_score,

        "ai_review": "\n".join(review_messages),

        "refactoring": "\n".join(refactoring_messages),

        "learning_mode": "\n".join(learning_messages),

    }