from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, Response
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import io
from datetime import datetime
from model.models import (
    db,
    ChildRegistration,
    CaseHistory,
    CounsellingSessions,
    CpiVisits,
    CspVisits,
    FamilyCounselling,
    GroupSessions,
    IndividualSessions,
    InitialAssessment,
    StaffCounselling,
    Users,
)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# IMPORTANT: Use the correct database name.
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://maria:haseeb@localhost/child_bearu"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://maria:haseeb@localhost/child_bearu"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://maria:your_password@localhost/childbearu'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure upload folder (ensure this directory exists)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize SQLAlchemy
db.init_app(app)

# Create tables if they do not exist
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user exists in the database
        user = Users.query.filter_by(username=username).first()

        if user and user.password == password:
            session["user"] = username
            # Assign role based on username
            session["role"] = "admin" if username.lower() == "admin" else "user"
            flash("Login Successful!", "success")

            # Redirect based on role
            if session["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("dashboard"))

        flash("Invalid username or password!", "danger")

    return render_template("login.html")  # Only show login page when needed

@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, no need to see register page
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Prevent registration of an "admin" user manually
        if username.lower() == "admin":
            flash("Cannot register as 'admin'.", "danger")
            return redirect(url_for("register"))

        # Check if user already exists
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        # Register the user with "user" role
        new_user = Users(username=username, password=password, role="user")
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    # Handle POST requests
    if request.method == "POST":
        print("POST request received!")  # Debugging print
        form_type = request.form.get("form_type")
        print("Form type:", form_type)  # Debugging print

        try:
            if form_type == "child_registration":
                child_name = request.form["childName"]
                father_name = request.form["fatherName"]
                admission_date = datetime.strptime(request.form["admissionDate"], "%Y-%m-%d").date()
                admission_location = request.form["admissionLocation"]

                # Handle file upload
                file = request.files.get("childPhoto")
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(file_path)
                else:
                    filename = None
                    file_path = None

                new_child = ChildRegistration(
                    child_name=child_name,
                    father_name=father_name,
                    admission_date=admission_date,
                    admission_location=admission_location,
                    child_photo=filename,
                    photo_path=file_path
                )
                db.session.add(new_child)
                db.session.commit()
                print("Child added successfully to DB!")
                flash(f"Child {child_name} registered successfully!", "success")

            elif form_type == "case_history":
                try:
                    # Ensure childId is provided and is valid
                    child_id = request.form.get("childId")
                    if not child_id or not child_id.isdigit():
                        flash("Error: Child ID is required for Case History.", "danger")
                        return redirect(url_for("dashboard"))

                    # Convert child_id to integer
                    child_id = int(child_id)

                    # Ensure the child exists in the database
                    child = ChildRegistration.query.get(child_id)

                    if not child:
                        flash("Error: Child does not exist.", "danger")
                        return redirect(url_for("dashboard"))

                    # Extract therapeutic history checkboxes (if any)
                    therapeutic_history = request.form.getlist("therapeuticHistory[]")
                    therapeutic_history_str = ", ".join(therapeutic_history) if therapeutic_history else "None"

                    new_case = CaseHistory(
                        child_id=child_id,
                        name=request.form["childName"],
                        gender=request.form["childGender"],
                        age=int(request.form["childAge"]),
                        admission_source=request.form["admissionSource"],
                        abuse_status=request.form.get("abuseStatus", "N/A"),
                        family_history=request.form.get("familyHistory", ""),
                        medical_history=request.form.get("medicalHistory", ""),
                        psychological_history=request.form.get("psychologicalHistory", ""),
                    )
                    db.session.add(new_case)
                    db.session.commit()
                    flash("Case history recorded successfully!", "success")

                except Exception as e:
                    db.session.rollback()
                    print("Error:", e)
                    flash("Error saving Case History: " + str(e), "danger")

            elif form_type == "counselling":
                new_counselling = CounsellingSessions(
                    child_id=request.form["childId"],
                    counsellor_name=request.form["counsellorName"],
                    session_date=datetime.strptime(request.form["sessionDate"], "%Y-%m-%d").date(),
                    session_notes=request.form["counsellingRemarks"],
                    outcomes=request.form["counsellingOutcomes"]
                )
                db.session.add(new_counselling)
                db.session.commit()
                flash("Counselling session recorded successfully!", "success")

            elif form_type == "individual_session":
                new_session = IndividualSessions(
                    session_name=request.form["sessionName"],
                    session_date=datetime.strptime(request.form["sessionDate"], "%Y-%m-%d").date(),
                    session_details=request.form["sessionDetails"]
                )
                db.session.add(new_session)
                db.session.commit()
                flash("Individual session recorded successfully!", "success")

            elif form_type == "group_session":
                new_group = GroupSessions(
                    child_one_name=request.form["child1Name"],
                    child_two_name=request.form.get("child2Name", ""),
                    child_three_name=request.form.get("child3Name", ""),
                    child_four_name=request.form.get("child4Name", ""),
                    session_details=request.form["groupSessionDetails"]
                )
                db.session.add(new_group)
                db.session.commit()
                flash("Group session recorded successfully!", "success")

            elif form_type == "family_counselling":
                new_family = FamilyCounselling(
                    family_name=request.form["familyName"],
                    father_name=request.form["fatherNameFamily"],
                    mother_name=request.form["motherNameFamily"],
                    session_details=request.form["familySessionDetails"]
                )
                db.session.add(new_family)
                db.session.commit()
                flash("Family counselling recorded successfully!", "success")

            elif form_type == "staff_counselling":
                new_staff = StaffCounselling(
                    staff_role=request.form["staffRole"],
                    session_activity=request.form["sessionActivity"]
                )
                db.session.add(new_staff)
                db.session.commit()
                flash("Staff counselling recorded successfully!", "success")

            elif form_type == "cpi_visit":
                new_cpi = CpiVisits(
                    visit_date=datetime.strptime(request.form["cpiDate"], "%Y-%m-%d").date()
                )
                db.session.add(new_cpi)
                db.session.commit()
                flash("CPI visit recorded successfully!", "success")

            elif form_type == "csp_visit":
                new_csp = CspVisits(
                    visit_date=datetime.strptime(request.form["cspDate"], "%Y-%m-%d").date()
                )
                db.session.add(new_csp)
                db.session.commit()
                flash("CSP visit recorded successfully!", "success")

            elif form_type == "initial_assessment":
                try:
                    child_id = request.form.get("childId")
                    if not child_id:
                        flash("Error: Child ID is required for Initial Assessment.", "danger")
                        return redirect(url_for("dashboard"))

                    child_id = int(child_id)
                    child = db.session.get(ChildRegistration, child_id)
                    if not child:
                        flash("Error: Child does not exist.", "danger")
                        return redirect(url_for("dashboard"))

                    registration_no = request.form["initialRegistrationNo"]
                    gender = request.form["initialGender"]
                    age = int(request.form["initialAge"]) if request.form["initialAge"] else None
                    religion = request.form["initialReligion"]
                    education = request.form["initialEducation"]
                    category = request.form["initialcatagory"]

                    birth_order = request.form.get("initialBirthOrder", "")
                    repeater = request.form.get("initialRepeater", "")
                    occupation = request.form.get("initialOccupation", "")
                    father_name = request.form["initialFamilyHistoryFatherName"]
                    father_occupation = request.form.get("initialFamilyHistoryFatherOccupation", "")
                    mother_name = request.form["initialFamilyHistoryMotherName"]
                    mother_occupation = request.form.get("initialFamilyHistoryMotherOccupation", "")
                    siblings_count = int(request.form["initialFamilyHistorySiblings"]) if request.form["initialFamilyHistorySiblings"] else 0
                    siblings_details = request.form.get("initialFamilyHistorySiblingsDetails", "")
                    relations_with_parents = request.form.get("initialFamilyHistoryRelationsWithParents", "")
                    home_address = request.form["initialHomeAddress"]
                    contact_no = request.form["initialContactNo"]
                    abuse_history = request.form.get("initialAbuseHistory", "")
                    significant_complaint = request.form.get("initialSignificantComplaint", "")
                    work_history = request.form.get("initialWorkHistory", "")
                    remarks = request.form.get("initialRemarks", "")
                    forward_to = request.form.get("initialForwardTo", None)

                    new_assessment = InitialAssessment(
                        child_id=child_id,
                        registration_no=registration_no,
                        gender=gender,
                        age=age,
                        religion=religion,
                        education=education,
                        birth_order=birth_order,
                        repeater=repeater,
                        occupation=occupation,
                        category=category,
                        father_name=father_name,
                        father_occupation=father_occupation,
                        mother_name=mother_name,
                        mother_occupation=mother_occupation,
                        siblings_count=siblings_count,
                        siblings_details=siblings_details,
                        relations_with_parents=relations_with_parents,
                        home_address=home_address,
                        contact_no=contact_no,
                        abuse_history=abuse_history,
                        significant_complaint=significant_complaint,
                        work_history=work_history,
                        remarks=remarks,
                        forward_to=forward_to
                    )
                    db.session.add(new_assessment)
                    db.session.commit()
                    flash("Initial Assessment recorded successfully!", "success")

                except Exception as e:
                    db.session.rollback()
                    print("Error:", e)
                    flash("Error saving Initial Assessment: " + str(e), "danger")

            else:
                flash("Unknown form type submitted.", "danger")

        except Exception as e:
            db.session.rollback()
            print("Error:", e)
            flash("Error processing form: " + str(e), "danger")

        return redirect(url_for("dashboard"))

    # ---- NEW LINE: fetch children for any forms that might need them
    children = ChildRegistration.query.all()
    # Finally, render the dashboard if GET or after POST
    return render_template("dashboard.html", children=children)

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

#############################
# ADMIN DASHBOARD ROUTE
#############################
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

#############################
# ADMIN - MANAGE FORMS
#############################
@app.route("/admin/manage_forms/<form_type>")
def manage_forms(form_type):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    form_models = {
        "child_registration": ChildRegistration,
        "initial_assessment": InitialAssessment,
        "case_history": CaseHistory,
        "counselling_sessions": CounsellingSessions,
        "individual_sessions": IndividualSessions,
        "group_sessions": GroupSessions,
        "family_counselling": FamilyCounselling,
        "staff_counselling": StaffCounselling,
        "cpi_visits": CpiVisits,
        "csp_visits": CspVisits
    }

    model = form_models.get(form_type)
    if not model:
        flash("Invalid form type!", "danger")
        return redirect(url_for("admin_dashboard"))

    records = model.query.all()
    return render_template("manage_forms.html", records=records, form_type=form_type)

@app.route("/admin/edit_form/<form_type>/<int:record_id>", methods=["GET", "POST"])
def edit_form(form_type, record_id):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    form_models = {
        "child_registration": ChildRegistration,
        "initial_assessment": InitialAssessment,  # <-- ADD THIS
        "case_history": CaseHistory,
        "counselling_sessions": CounsellingSessions,  # <-- AND THIS
        "individual_sessions": IndividualSessions,
        "group_sessions": GroupSessions,
        "family_counselling": FamilyCounselling,
        "staff_counselling": StaffCounselling,
        "cpi_visits": CpiVisits,
        "csp_visits": CspVisits
    }

    model = form_models.get(form_type)
    record = model.query.get_or_404(record_id)

    if request.method == "POST":
        for field in request.form:
            setattr(record, field, request.form[field])
        db.session.commit()
        flash("Record updated successfully!", "success")
        return redirect(url_for("manage_forms", form_type=form_type))

    return render_template("edit_form.html", record=record, form_type=form_type)

@app.route("/admin/delete_form/<form_type>/<int:record_id>")
def delete_form(form_type, record_id):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    form_models = {
        "child_registration": ChildRegistration,
        "initial_assessment": InitialAssessment,  # <-- ADD THIS
        "case_history": CaseHistory,
        "counselling_sessions": CounsellingSessions,  # <-- AND THIS
        "individual_sessions": IndividualSessions,
        "group_sessions": GroupSessions,
        "family_counselling": FamilyCounselling,
        "staff_counselling": StaffCounselling,
        "cpi_visits": CpiVisits,
        "csp_visits": CspVisits
    }
    model = form_models.get(form_type)
    record = model.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash("Record deleted successfully!", "success")
    return redirect(url_for("manage_forms", form_type=form_type))

@app.route("/admin/generate_pdf/<form_type>/<int:record_id>")
def generate_pdf(form_type, record_id):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    form_models = {
        "child_registration": ChildRegistration,
        "initial_assessment": InitialAssessment,  # <-- ADD THIS
        "case_history": CaseHistory,
        "counselling_sessions": CounsellingSessions,  # <-- AND THIS
        "individual_sessions": IndividualSessions,
        "group_sessions": GroupSessions,
        "family_counselling": FamilyCounselling,
        "staff_counselling": StaffCounselling,
        "cpi_visits": CpiVisits,
        "csp_visits": CspVisits
    }
    model = form_models.get(form_type)
    record = model.query.get_or_404(record_id)

    # Create a byte-stream buffer for PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Write PDF Title
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, 750, f"{form_type.replace('_', ' ').title()} Record")

    # Write Record Data
    y = 720
    pdf.setFont("Helvetica", 12)
    for field, value in record.__dict__.items():
        if not field.startswith("_"):
            pdf.drawString(100, y, f"{field}: {value}")
            y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    # Create Flask Response with PDF
    response = make_response(buffer.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={form_type}_record_{record.id}.pdf"
    response.mimetype = "application/pdf"

    return response

# Generate Report on Start date and End Date
# from flask import make_response, request
# from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# @app.route("/admin/generate_pdf_DateWise/<form_type>")
# def generate_pdf_DateWise(form_type):
#     if "user" not in session or session.get("role") != "admin":
#         return redirect(url_for("login"))

#     # Get the start_date and end_date from request arguments (if provided)
#     start_date = request.args.get("start_date")
#     end_date = request.args.get("end_date")

#     if not start_date or not end_date:
#         return "Start date and End date are required.", 400

#     form_models = {
#         "child_registration": ChildRegistration,
#         "initial_assessment": InitialAssessment,
#         "case_history": CaseHistory,
#         "counselling_sessions": CounsellingSessions,
#         "individual_sessions": IndividualSessions,
#         "group_sessions": GroupSessions,
#         "family_counselling": FamilyCounselling,
#         "staff_counselling": StaffCounselling,
#         "cpi_visits": CpiVisits,
#         "csp_visits": CspVisits
#     }

#     model = form_models.get(form_type)
#     if not model:
#         return "Invalid form type", 400

#     # Filter records by the created_at date range
#     records = model.query.filter(model.created_at >= start_date, model.created_at <= end_date).all()

#     if not records:
#         return "No records found in the selected date range.", 404

#     # Create a byte-stream buffer for PDF
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     # Write PDF Title
#     pdf.setFont("Helvetica-Bold", 14)
#     pdf.drawString(200, 750, f"{form_type.replace('_', ' ').title()} Records")

#     # Write Record Data
#     y = 720
#     pdf.setFont("Helvetica", 12)
#     for record in records:
#         pdf.drawString(100, y, f"Record ID: {record.id}")
#         y -= 20
#         for field, value in record.__dict__.items():
#             if not field.startswith("_"):
#                 pdf.drawString(100, y, f"{field}: {value}")
#                 y -= 20

#             if y < 50:  # If space is running out on the page, add a new page
#                 pdf.showPage()
#                 y = 750

#         y -= 10  # Space between records

#     pdf.showPage()
#     pdf.save()
#     buffer.seek(0)

#     # Create Flask Response with PDF
#     response = make_response(buffer.getvalue())
#     response.headers["Content-Disposition"] = f"attachment; filename={form_type}_report_{start_date}_to_{end_date}.pdf"
#     response.mimetype = "application/pdf"

#     return response

from flask import make_response, request, redirect, url_for, session
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak

@app.route("/admin/generate_pdf_DateWise/<form_type>")
def generate_pdf_DateWise(form_type):
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return "Start date and End date are required.", 400

    form_models = {
        "child_registration": ChildRegistration,
        "initial_assessment": InitialAssessment,
        "case_history": CaseHistory,
        "counselling_sessions": CounsellingSessions,
        "individual_sessions": IndividualSessions,
        "group_sessions": GroupSessions,
        "family_counselling": FamilyCounselling,
        "staff_counselling": StaffCounselling,
        "cpi_visits": CpiVisits,
        "csp_visits": CspVisits
    }

    model = form_models.get(form_type)
    if not model:
        return "Invalid form type", 400

    records = model.query.filter(model.created_at >= start_date, model.created_at <= end_date).all()

    if not records:
        return "No records found in the selected date range.", 404

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Add Title
    elements.append(Paragraph(f"<b>{form_type.replace('_', ' ').title()} Records</b>", title_style))

    for idx, record in enumerate(records):
        record_data = []
        fields = [(field, str(value)) for field, value in record.__dict__.items() if not field.startswith("_")]

        # Group fields 3 fields per row
        row = []
        for i, (field, value) in enumerate(fields, 1):
            row.append(field)
            row.append(value)
            if i % 2 == 0:
                record_data.append(row)
                row = []

        # If leftover fields (less than 3 at end)
        if row:
            # Fill empty fields to complete 6 columns
            while len(row) < 4:
                row.append('')
            record_data.append(row)

        # Create table
        table = Table(record_data, colWidths=[150, 150, 150, 150],rowHeights=30)

        # Table styling
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, (0,0,0)),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,-1), (1,1,1)),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))

        elements.append(Paragraph(f"<b>Record ID: {record.id}</b>", normal_style))
        elements.append(table)

        # Add page break after every record except the last one
        if idx != len(records) - 1:
            elements.append(PageBreak())

    # Build document
    doc.build(elements)

    buffer.seek(0)

    # Return response
    response = make_response(buffer.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={form_type}_report_{start_date}_to_{end_date}.pdf"
    response.mimetype = "application/pdf"

    return response







if __name__ == "__main__":
    app.run(debug=True)
