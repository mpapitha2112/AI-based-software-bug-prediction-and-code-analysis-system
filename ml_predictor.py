import os
import joblib
import pandas as pd


# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml_models",
    "bug_prediction_model.pkl"
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

_model_data = None


def load_model():
    """
    Load the trained machine learning model.
    """

    global _model_data

    if _model_data is None:

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                "ML model not found. "
                "Please run train_model.py first."
            )

        _model_data = joblib.load(
            MODEL_PATH
        )

    return _model_data


# ============================================================
# EXTRACT CODE FEATURES
# ============================================================

def extract_features(code):
    """
    Extract software metrics from Python source code.

    These features correspond to the features
    used while training the ML model.
    """

    lines = code.splitlines()

    # Remove empty lines
    non_empty_lines = [
        line for line in lines
        if line.strip()
    ]

    loc = len(non_empty_lines)

    # --------------------------------------------------------
    # Count functions
    # --------------------------------------------------------

    function_count = sum(
        1
        for line in lines
        if line.strip().startswith("def ")
    )

    # --------------------------------------------------------
    # Count classes
    # --------------------------------------------------------

    class_count = sum(
        1
        for line in lines
        if line.strip().startswith("class ")
    )

    # --------------------------------------------------------
    # Count loops
    # --------------------------------------------------------

    loop_count = sum(
        1
        for line in lines
        if (
            line.strip().startswith("for ")
            or
            line.strip().startswith("while ")
        )
    )

    # --------------------------------------------------------
    # Count conditional statements
    # --------------------------------------------------------

    condition_count = sum(
        1
        for line in lines
        if line.strip().startswith("if ")
    )

    # --------------------------------------------------------
    # Count branches
    # --------------------------------------------------------

    branch_count = (
        loop_count
        +
        condition_count
    )

    # --------------------------------------------------------
    # Count operators
    # --------------------------------------------------------

    operators = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "==",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
        "=",
        "and",
        "or",
        "not"
    ]

    operator_count = 0

    for line in lines:

        for operator in operators:

            operator_count += line.count(
                operator
            )

    # --------------------------------------------------------
    # Count operands
    # --------------------------------------------------------

    operand_count = sum(
        len(line.split())
        for line in lines
    )

    # --------------------------------------------------------
    # Approximate cyclomatic complexity
    # --------------------------------------------------------

    cyclomatic = (
        1
        +
        condition_count
        +
        loop_count
    )

    # --------------------------------------------------------
    # Program length
    # --------------------------------------------------------

    length = (
        operator_count
        +
        operand_count
    )

    # --------------------------------------------------------
    # Program volume
    # --------------------------------------------------------

    volume = (
        length
        if length > 0
        else 1
    )

    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    difficulty = (
        cyclomatic
        /
        max(function_count + 1, 1)
    )

    # --------------------------------------------------------
    # Fan-in / Fan-out approximation
    # --------------------------------------------------------

    fan_in = function_count

    fan_out = (
        function_count
        +
        class_count
    )

    return {
        "LOC": loc,
        "CYCLO": cyclomatic,
        "LENGTH": length,
        "VOLUME": volume,
        "DIFFICULTY": difficulty,
        "INT_FAN_IN": fan_in,
        "INT_FAN_OUT": fan_out,
        "NUM_OPERATORS": operator_count,
        "NUM_OPERANDS": operand_count,
        "BRANCH_COUNT": branch_count,
    }


# ============================================================
# NORMALIZE FEATURES
# ============================================================

def normalize_features(features):
    """
    Convert extracted code metrics into a format
    suitable for the trained model.

    The training dataset uses normalized values,
    therefore the uploaded code metrics are scaled
    using simple bounded normalization.
    """

    normalized = {

        "LOC": min(
            features["LOC"] / 500,
            1.0
        ),

        "CYCLO": min(
            features["CYCLO"] / 50,
            1.0
        ),

        "LENGTH": min(
            features["LENGTH"] / 1000,
            1.0
        ),

        "VOLUME": min(
            features["VOLUME"] / 1000,
            1.0
        ),

        "DIFFICULTY": min(
            features["DIFFICULTY"] / 50,
            1.0
        ),

        "INT_FAN_IN": min(
            features["INT_FAN_IN"] / 50,
            1.0
        ),

        "INT_FAN_OUT": min(
            features["INT_FAN_OUT"] / 50,
            1.0
        ),

        "NUM_OPERATORS": min(
            features["NUM_OPERATORS"] / 500,
            1.0
        ),

        "NUM_OPERANDS": min(
            features["NUM_OPERANDS"] / 500,
            1.0
        ),

        "BRANCH_COUNT": min(
            features["BRANCH_COUNT"] / 50,
            1.0
        ),
    }

    return normalized


# ============================================================
# PREDICT BUG RISK
# ============================================================

def predict_bug_risk(code):
    """
    Predict whether the uploaded Python code
    is likely to contain defects.
    """

    model_data = load_model()

    model = model_data["model"]

    feature_names = model_data["features"]

    # Extract metrics
    features = extract_features(code)

    # Normalize metrics
    normalized = normalize_features(
        features
    )

    # Create DataFrame in exactly the
    # same feature order used during training.
    input_data = pd.DataFrame(
        [
            [
                normalized[name]
                for name in feature_names
            ]
        ],
        columns=feature_names
    )

    # ML prediction
    prediction = model.predict(
        input_data
    )[0]

    # Probability
    probabilities = model.predict_proba(
        input_data
    )[0]

    confidence = float(
        max(probabilities) * 100
    )

    # --------------------------------------------------------
    # Convert prediction to readable result
    # --------------------------------------------------------

    if int(prediction) == 1:

        risk = "High"

    else:

        risk = "Low"

    return {
        "prediction": int(prediction),
        "risk": risk,
        "confidence": round(
            confidence,
            2
        ),
        "features": features,
    }