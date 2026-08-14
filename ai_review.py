import ast
import re


def generate_ai_review(code):
    """
    Generate a rule-based AI-style code review.

    The uploaded Python code is analyzed statically.
    It is never executed.
    """

    review_points = []
    refactoring_points = []
    learning_points = []

    # =========================================================
    # Parse Python code
    # =========================================================

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "review": (
                "The uploaded Python file contains a syntax error. "
                "Fix the syntax before performing a complete review."
            ),
            "refactoring": (
                "Check brackets, indentation, missing colons, "
                "and other Python syntax problems."
            ),
            "learning": (
                "Syntax errors prevent Python from understanding "
                "the program correctly."
            ),
        }

    # =========================================================
    # Basic code statistics
    # =========================================================

    lines = code.splitlines()

    non_empty_lines = [
        line for line in lines
        if line.strip()
    ]

    total_lines = len(non_empty_lines)

    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]

    # =========================================================
    # 1. Function documentation
    # =========================================================

    undocumented_functions = []

    for function in functions:
        if ast.get_docstring(function) is None:
            undocumented_functions.append(function.name)

    if undocumented_functions:
        review_points.append(
            "Some functions do not have documentation. "
            "Adding short docstrings would improve readability."
        )

        refactoring_points.append(
            "Add docstrings to important functions such as: "
            + ", ".join(undocumented_functions[:5])
        )

        learning_points.append(
            "A docstring explains the purpose of a function "
            "and makes code easier for other developers to understand."
        )
    elif functions:
        review_points.append(
            "Functions contain documentation, which improves "
            "code readability."
        )

    # =========================================================
    # 2. Long functions
    # =========================================================

    long_functions = []

    for function in functions:
        function_length = (
            function.end_lineno - function.lineno + 1
        )

        if function_length > 30:
            long_functions.append(function.name)

    if long_functions:
        review_points.append(
            "Some functions are relatively long and may be "
            "difficult to maintain."
        )

        refactoring_points.append(
            "Consider splitting long functions into smaller "
            "functions: "
            + ", ".join(long_functions[:5])
        )

        learning_points.append(
            "Smaller functions usually make programs easier "
            "to test, understand, and maintain."
        )

    # =========================================================
    # 3. Hardcoded credentials
    # =========================================================

    credential_pattern = re.compile(
        r"(password|passwd|pwd|api_key|apikey|secret_key)"
        r"\s*=\s*['\"][^'\"]+['\"]",
        re.IGNORECASE,
    )

    if credential_pattern.search(code):
        review_points.append(
            "A possible hardcoded credential was detected."
        )

        refactoring_points.append(
            "Move passwords, API keys, and secrets into "
            "environment variables or secure configuration."
        )

        learning_points.append(
            "Hardcoded credentials can accidentally be exposed "
            "when source code is shared or uploaded to repositories."
        )

    # =========================================================
    # 4. Dangerous system commands
    # =========================================================

    if re.search(
        r"\bos\.system\s*\(",
        code,
    ):
        review_points.append(
            "os.system() was detected. This can create security "
            "risks when commands contain untrusted input."
        )

        refactoring_points.append(
            "Replace os.system() with safer subprocess usage "
            "and validate command arguments."
        )

        learning_points.append(
            "Operating-system commands should be handled carefully "
            "because unsafe input can lead to command injection."
        )

    # =========================================================
    # 5. Weak hashing
    # =========================================================

    if re.search(
        r"(hashlib\.md5|hashlib\.sha1)",
        code,
        re.IGNORECASE,
    ):
        review_points.append(
            "Weak hashing such as MD5 or SHA1 was detected."
        )

        refactoring_points.append(
            "Use a modern cryptographic algorithm appropriate "
            "for the security requirement."
        )

        learning_points.append(
            "MD5 and SHA1 are considered weak for many "
            "security-sensitive applications."
        )

    # =========================================================
    # 6. eval / exec
    # =========================================================

    if re.search(
        r"\b(eval|exec)\s*\(",
        code,
    ):
        review_points.append(
            "Dynamic code execution using eval() or exec() "
            "was detected."
        )

        refactoring_points.append(
            "Avoid eval() and exec() when possible and use "
            "safer alternatives."
        )

        learning_points.append(
            "eval() and exec() can execute dynamically supplied "
            "code and should be used with extreme caution."
        )

    # =========================================================
    # 7. Too many imports
    # =========================================================

    if len(imports) > 10:
        review_points.append(
            "The file contains a large number of imports."
        )

        refactoring_points.append(
            "Remove unused imports and organize imports "
            "according to their purpose."
        )

        learning_points.append(
            "Keeping imports organized and removing unused "
            "dependencies makes code easier to maintain."
        )

    # =========================================================
    # 8. Very long source file
    # =========================================================

    if total_lines > 300:
        review_points.append(
            "The source file is relatively large."
        )

        refactoring_points.append(
            "Consider dividing large functionality into "
            "separate modules."
        )

        learning_points.append(
            "Splitting large programs into modules improves "
            "maintainability and organization."
        )

    # =========================================================
    # 9. Missing comments
    # =========================================================

    comments = [
        line
        for line in lines
        if line.strip().startswith("#")
    ]

    if total_lines > 20 and len(comments) == 0:
        review_points.append(
            "The source code contains no comments."
        )

        refactoring_points.append(
            "Add meaningful comments for complex logic, "
            "but avoid unnecessary comments."
        )

        learning_points.append(
            "Comments are useful for explaining complex logic "
            "that may not be immediately obvious."
        )

    # =========================================================
    # 10. General positive feedback
    # =========================================================

    if not review_points:
        review_points.append(
            "The code structure looks clean based on the "
            "current static review rules."
        )

    # =========================================================
    # Build review text
    # =========================================================

    review_text = "AI Code Review\n\n"

    for number, point in enumerate(review_points, start=1):
        review_text += f"{number}. {point}\n"

    # =========================================================
    # Build refactoring text
    # =========================================================

    if refactoring_points:
        refactoring_text = "Refactoring Suggestions\n\n"

        for number, point in enumerate(
            refactoring_points,
            start=1,
        ):
            refactoring_text += f"{number}. {point}\n"
    else:
        refactoring_text = (
            "No major refactoring suggestions were "
            "identified by the current rules."
        )

    # =========================================================
    # Build learning text
    # =========================================================

    if learning_points:
        learning_text = "Smart Learning Mode\n\n"

        for number, point in enumerate(
            learning_points,
            start=1,
        ):
            learning_text += f"{number}. {point}\n"
    else:
        learning_text = (
            "Your code passed the current learning checks. "
            "Continue following clean-code practices."
        )

    # =========================================================
    # Return results
    # =========================================================

    return {
        "review": review_text,
        "refactoring": refactoring_text,
        "learning": learning_text,
    }