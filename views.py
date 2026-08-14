from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import CodeAnalysis
from .utils import analyze_python_code
from .security_analyzer import analyze_security
from .ai_review import generate_ai_review


# =========================================================
# HOME
# =========================================================

def home(request):
    return render(request, "home.html")


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # Username validation
        # -------------------------------------------------

        if not username:

            return render(
                request,
                "register.html",
                {
                    "error": "Please enter a username."
                }
            )

        # -------------------------------------------------
        # Password validation
        # -------------------------------------------------

        if not password:

            return render(
                request,
                "register.html",
                {
                    "error": "Please enter a password."
                }
            )

        # -------------------------------------------------
        # Confirm password
        # -------------------------------------------------

        if password != confirm_password:

            return render(
                request,
                "register.html",
                {
                    "error": "Passwords do not match."
                }
            )

        # -------------------------------------------------
        # Check existing username
        # -------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "register.html",
                {
                    "error": "Username already exists."
                }
            )

        # -------------------------------------------------
        # Create user
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.save()

        # -------------------------------------------------
        # Login automatically
        # -------------------------------------------------

        login(
            request,
            user
        )

        return redirect("dashboard")

    return render(
        request,
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # Validate login fields
        # -------------------------------------------------

        if not username or not password:

            return render(
                request,
                "login.html",
                {
                    "error": "Please enter username and password."
                }
            )

        # -------------------------------------------------
        # Authenticate user
        # -------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect("dashboard")

        return render(
            request,
            "login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def user_logout(request):

    logout(request)

    return redirect("login")


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    analyses = CodeAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "dashboard.html",
        {
            "analyses": analyses
        }
    )


# =========================================================
# UPLOAD AND ANALYZE CODE
# =========================================================

@login_required
def upload_code(request):
    """
    Upload and analyze a Python source file.

    Analysis includes:
    - ML bug prediction
    - Code quality
    - Security analysis
    - AI code review
    - Refactoring suggestions
    - Smart learning mode
    """

    if request.method == "POST":

        # =================================================
        # PROJECT NAME
        # =================================================

        project_name = request.POST.get(
            "project_name",
            ""
        ).strip()

        # =================================================
        # FILE
        # =================================================

        code_file = request.FILES.get(
            "code_file"
        )

        # =================================================
        # PROJECT NAME VALIDATION
        # =================================================

        if not project_name:

            return render(
                request,
                "upload.html",
                {
                    "error": "Please enter a project name."
                }
            )

        # =================================================
        # FILE VALIDATION
        # =================================================

        if not code_file:

            return render(
                request,
                "upload.html",
                {
                    "error": "Please select a Python file."
                }
            )

        # =================================================
        # PYTHON FILE VALIDATION
        # =================================================

        if not code_file.name.lower().endswith(".py"):

            return render(
                request,
                "upload.html",
                {
                    "error": "Only Python (.py) files are allowed."
                }
            )

        # =================================================
        # READ SOURCE CODE
        # =================================================

        try:

            code = code_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        except Exception:

            return render(
                request,
                "upload.html",
                {
                    "error": "Unable to read the uploaded file."
                }
            )

        # =================================================
        # EMPTY FILE CHECK
        # =================================================

        if not code.strip():

            return render(
                request,
                "upload.html",
                {
                    "error": "The uploaded Python file is empty."
                }
            )

        # =================================================
        # ML CODE ANALYSIS
        # =================================================

        try:

            result = analyze_python_code(
                code
            )

        except Exception as error:

            return render(
                request,
                "upload.html",
                {
                    "error": (
                        "Code analysis failed: "
                        + str(error)
                    )
                }
            )

        # =================================================
        # SECURITY ANALYSIS
        # =================================================

        try:

            security_result = analyze_security(
                code
            )

        except Exception:

            security_result = {
                "security_score": 100,
                "security_risk": "Low",
                "security_issues": []
            }

        # =================================================
        # AI CODE REVIEW
        # =================================================

        try:

            ai_result = generate_ai_review(
                code
            )

        except Exception:

            ai_result = {
                "review": (
                    "AI code review could not be generated."
                ),
                "refactoring": (
                    "No refactoring suggestions available."
                ),
                "learning": (
                    "No learning explanation available."
                )
            }

        # =================================================
        # SECURITY VALUES
        # =================================================

        security_score = security_result.get(
            "security_score",
            100
        )

        security_risk = security_result.get(
            "security_risk",
            "Low"
        )

        security_issues = security_result.get(
            "security_issues",
            []
        )

        # =================================================
        # ML VALUES
        # =================================================

        bug_risk = result.get(
            "bug_risk",
            "Low"
        )

        quality_score = result.get(
            "quality_score",
            0
        )

        health_score = result.get(
            "health_score",
            0
        )

        # =================================================
        # AI REVIEW VALUES
        # =================================================

        ai_review = ai_result.get(
            "review",
            ""
        )

        refactoring = ai_result.get(
            "refactoring",
            ""
        )

        learning_mode = ai_result.get(
            "learning",
            ""
        )

        # =================================================
        # CALCULATE OVERALL SCORE
        # =================================================

        try:

            overall_score = (
                int(quality_score)
                + int(security_score)
                + int(health_score)
            ) / 3

        except (TypeError, ValueError):

            overall_score = 0

        # =================================================
        # ACHIEVEMENT
        # =================================================

        if overall_score >= 90:

            achievement = "Expert"

        elif overall_score >= 75:

            achievement = "Advanced"

        elif overall_score >= 60:

            achievement = "Intermediate"

        else:

            achievement = "Beginner"

        # =================================================
        # SAVE ANALYSIS
        # =================================================

        analysis = CodeAnalysis.objects.create(

            user=request.user,

            project_name=project_name,

            python_file=code_file,

            bug_risk=bug_risk,

            quality_score=quality_score,

            security_score=security_score,

            health_score=health_score,

            ai_review=ai_review,

            refactoring=refactoring,

            learning_mode=learning_mode,

            achievement=achievement
        )

        # =================================================
        # STORE SECURITY INFORMATION
        #
        # Kept for compatibility with your existing project.
        # The result page will now primarily use the values
        # belonging to the current analysis.
        # =================================================

        request.session[
            "last_security_risk"
        ] = security_risk

        request.session[
            "last_security_issues"
        ] = security_issues

        # =================================================
        # REDIRECT TO RESULT PAGE
        # =================================================

        return redirect(
            "result",
            analysis_id=analysis.id
        )

    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "upload.html"
    )


# =========================================================
# RESULT PAGE
# =========================================================

@login_required
def result(request, analysis_id):

    # =====================================================
    # GET CURRENT USER'S ANALYSIS
    # =====================================================

    analysis = get_object_or_404(
        CodeAnalysis,
        id=analysis_id,
        user=request.user
    )

    # =====================================================
    # SECURITY INFORMATION
    #
    # These are still retrieved from session because your
    # current CodeAnalysis model does not appear to contain
    # security_risk and security_issues fields.
    # =====================================================

    security_risk = request.session.get(
        "last_security_risk",
        "Low"
    )

    security_issues = request.session.get(
        "last_security_issues",
        []
    )

    # =====================================================
    # RESULT VALUES
    # =====================================================

    bug_risk = analysis.bug_risk

    quality_score = analysis.quality_score

    security_score = analysis.security_score

    health_score = analysis.health_score

    ai_review = analysis.ai_review

    refactoring = analysis.refactoring

    learning_mode = analysis.learning_mode

    achievement = analysis.achievement

    # =====================================================
    # RESULT PAGE CONTEXT
    # =====================================================

    context = {

        # Main database object
        "analysis": analysis,

        # Bug prediction
        "bug_risk": bug_risk,

        # Scores
        "quality_score": quality_score,

        "security_score": security_score,

        "health_score": health_score,

        # Security
        "security_risk": security_risk,

        "security_issues": security_issues,

        # AI Code Review
        "ai_review": ai_review,

        # Refactoring
        "refactoring": refactoring,

        # Smart Learning
        "learning": learning_mode,

        # Keep compatibility with older template
        "learning_mode": learning_mode,

        # Achievement
        "achievement": achievement,
    }

    return render(
        request,
        "result.html",
        context
    )