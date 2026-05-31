from flask import Blueprint, current_app, render_template, request
from app.routes.auth import login_required, biometrics_required, role_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    return render_template("dashboard.html")


@dashboard_bp.route("/dashboards")
@login_required
def dashboards():
    return render_template(
        "dashboards.html",
        power_bi_embeds=current_app.config.get("POWER_BI_EMBEDS", []),
    )


@dashboard_bp.route("/history")
@login_required
@role_required("wellness_manager", "assistant", "intern")
def history():
    return render_template("history.html")


@dashboard_bp.route("/employee-status")
@login_required
def employee_status():
    category = request.args.get("category", "overdue")
    return render_template("employee_status.html", initial_category=category)


@dashboard_bp.route("/conflicts")
@login_required
@role_required("wellness_manager", "assistant", "intern")
def conflicts():
    return render_template("conflicts.html")


@dashboard_bp.route("/change-log")
@login_required
@role_required("wellness_manager", "assistant", "intern")
def change_log():
    source = request.args.get("source", "all")
    return render_template("change_log.html", initial_source=source)


@dashboard_bp.route("/biometrics")
@login_required
@biometrics_required
def biometrics():
    return render_template("Biometrics_page.html")
