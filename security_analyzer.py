import ast
import re


def analyze_security(code):
    """
    Analyze Python source code for common security risks.

    Returns:
        {
            "score": int,
            "risk_level": str,
            "issues": list
        }
    """

    issues = []

    # ---------------------------------------------------------
    # 1. eval()
    # ---------------------------------------------------------

    if re.search(r"\beval\s*\(", code):
        issues.append({
            "type": "Dangerous Function",
            "severity": "High",
            "message": (
                "eval() can execute dynamically supplied Python code "
                "and may allow code injection."
            ),
            "suggestion": (
                "Avoid eval(). Use safer alternatives such as "
                "literal_eval() when appropriate."
            )
        })

    # ---------------------------------------------------------
    # 2. exec()
    # ---------------------------------------------------------

    if re.search(r"\bexec\s*\(", code):
        issues.append({
            "type": "Dangerous Function",
            "severity": "High",
            "message": (
                "exec() can execute arbitrary Python code."
            ),
            "suggestion": (
                "Avoid exec() and use explicit functions or "
                "controlled operations instead."
            )
        })

    # ---------------------------------------------------------
    # 3. Hardcoded password
    # ---------------------------------------------------------

    password_pattern = re.compile(
        r"(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
        re.IGNORECASE
    )

    if password_pattern.search(code):
        issues.append({
            "type": "Hardcoded Credential",
            "severity": "High",
            "message": (
                "A password appears to be directly stored in "
                "the source code."
            ),
            "suggestion": (
                "Use environment variables or a secure secret "
                "management system."
            )
        })

    # ---------------------------------------------------------
    # 4. Hardcoded API key / secret
    # ---------------------------------------------------------

    secret_pattern = re.compile(
        r"(api_key|apikey|secret_key|access_token)"
        r"\s*=\s*['\"][^'\"]+['\"]",
        re.IGNORECASE
    )

    if secret_pattern.search(code):
        issues.append({
            "type": "Hardcoded Secret",
            "severity": "High",
            "message": (
                "A possible API key or secret is stored directly "
                "inside the source code."
            ),
            "suggestion": (
                "Store secrets in environment variables or "
                "a secure secret manager."
            )
        })

    # ---------------------------------------------------------
    # 5. Dangerous subprocess usage
    # ---------------------------------------------------------

    if re.search(
        r"subprocess\.(run|call|Popen|check_output).*shell\s*=\s*True",
        code,
        re.IGNORECASE
    ):
        issues.append({
            "type": "Command Injection Risk",
            "severity": "High",
            "message": (
                "subprocess is being used with shell=True, "
                "which can increase command injection risk."
            ),
            "suggestion": (
                "Avoid shell=True when possible and pass commands "
                "as a list of arguments."
            )
        })

    # ---------------------------------------------------------
    # 6. os.system()
    # ---------------------------------------------------------

    if re.search(r"\bos\.system\s*\(", code):
        issues.append({
            "type": "Command Execution",
            "severity": "Medium",
            "message": (
                "os.system() executes operating-system commands "
                "and can become dangerous with untrusted input."
            ),
            "suggestion": (
                "Prefer subprocess with safe argument handling."
            )
        })

    # ---------------------------------------------------------
    # 7. Weak hash algorithms
    # ---------------------------------------------------------

    if re.search(
        r"(md5|sha1)\s*\(",
        code,
        re.IGNORECASE
    ):
        issues.append({
            "type": "Weak Cryptography",
            "severity": "Medium",
            "message": (
                "MD5 or SHA1 may be unsuitable for security-sensitive "
                "password or integrity operations."
            ),
            "suggestion": (
                "Use modern cryptographic algorithms appropriate "
                "for the security requirement."
            )
        })

    # ---------------------------------------------------------
    # 8. Pickle usage
    # ---------------------------------------------------------

    if re.search(
        r"pickle\.loads?\s*\(",
        code,
        re.IGNORECASE
    ):
        issues.append({
            "type": "Unsafe Deserialization",
            "severity": "High",
            "message": (
                "Loading untrusted data with pickle can lead to "
                "arbitrary code execution."
            ),
            "suggestion": (
                "Do not deserialize untrusted pickle data. "
                "Use safer data formats such as JSON where possible."
            )
        })

    # ---------------------------------------------------------
    # 9. SQL string formatting
    # ---------------------------------------------------------

    sql_pattern = re.compile(
        r"(SELECT|INSERT|UPDATE|DELETE).*"
        r"(%s|\.format\s*\(|f['\"])",
        re.IGNORECASE
    )

    if sql_pattern.search(code):
        issues.append({
            "type": "Possible SQL Injection",
            "severity": "High",
            "message": (
                "SQL statements appear to be constructed using "
                "string formatting."
            ),
            "suggestion": (
                "Use parameterized queries or your framework's "
                "ORM instead of building SQL strings manually."
            )
        })

    # ---------------------------------------------------------
    # 10. Parse the Python code
    # ---------------------------------------------------------

    try:
        ast.parse(code)

    except SyntaxError:
        issues.append({
            "type": "Syntax Problem",
            "severity": "Medium",
            "message": (
                "The uploaded Python source contains a syntax error."
            ),
            "suggestion": (
                "Correct the syntax before running the program."
            )
        })

    # ---------------------------------------------------------
    # Calculate security score
    # ---------------------------------------------------------

    score = 100

    for issue in issues:

        if issue["severity"] == "High":
            score -= 20

        elif issue["severity"] == "Medium":
            score -= 10

        else:
            score -= 5

    score = max(0, score)

    # ---------------------------------------------------------
    # Determine overall risk
    # ---------------------------------------------------------

    high_count = sum(
        1 for issue in issues
        if issue["severity"] == "High"
    )

    medium_count = sum(
        1 for issue in issues
        if issue["severity"] == "Medium"
    )

    if high_count > 0:
        risk_level = "High"

    elif medium_count > 0:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    return {
        "score": score,
        "risk_level": risk_level,
        "issues": issues
    }