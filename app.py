"""
PawCare – Pet Disease Detection System
Main Flask application entry point.

Handles MySQL connection, user authentication (register,
login, logout), and protected dashboard access.
"""

import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# ----------------------------------------------------------
# Flask Configuration (loaded from .env)
# ----------------------------------------------------------
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")

# Initialize Flask-MySQLdb connection
mysql = MySQL(app)


# ----------------------------------------------------------
# Authentication Helper – Login Required Decorator
# Protects routes that require an active user session.
# ----------------------------------------------------------
def login_required(view_func):
    """Redirect unauthenticated users to the login page."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


# ----------------------------------------------------------
# Landing Page
# ----------------------------------------------------------
@app.route("/")
def index():
    """Render the main landing page."""
    return render_template("index.html")


# ----------------------------------------------------------
# Database Test Route
# ----------------------------------------------------------
@app.route("/test-db")
def test_db():
    """Test MySQL connectivity by running SELECT DATABASE()."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        cursor.close()
        database_name = result[0]
        return f"Connected successfully to database: {database_name}"
    except Exception as error:
        return str(error)


# ----------------------------------------------------------
# Register – GET and POST
# ----------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  – Show the registration form.
    POST – Validate input, hash password, save new user.
    """
    # Already logged in → go to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Server-side validation – empty fields
        if not full_name or not email or not password or not confirm_password:
            flash("All fields are required. Please fill in every field.", "error")
            return render_template("register.html")

        # Server-side validation – password match
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return render_template("register.html")

        # Server-side validation – minimum password length
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        cursor = mysql.connection.cursor()

        # Check for duplicate email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            flash("This email is already registered. Please log in instead.", "error")
            return render_template("register.html")

        # Hash password – never store plain text
        hashed_password = generate_password_hash(password)

        # Insert new user into database
        cursor.execute(
            "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
            (full_name, email, hashed_password),
        )
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ----------------------------------------------------------
# Login – GET and POST
# ----------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  – Show the login form.
    POST – Verify credentials and create a user session.
    """
    # Already logged in → go to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Server-side validation – empty fields
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT user_id, full_name, password FROM users WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()

        # Verify credentials using hashed password comparison
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["full_name"] = user[1]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password. Please try again.", "error")
        return render_template("login.html")

    return render_template("login.html")


# ----------------------------------------------------------
# Logout
# ----------------------------------------------------------
@app.route("/logout")
def logout():
    """Clear the session and redirect to the login page."""
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# ----------------------------------------------------------
# Dashboard – Protected Route
# ----------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    """
    Protected dashboard page.
    Only accessible to authenticated users.
    """
    return render_template("dashboard.html", full_name=session.get("full_name"))


# ----------------------------------------------------------
# Add Pet – GET and POST
# ----------------------------------------------------------
@app.route("/pets/add", methods=["GET", "POST"])
@login_required
def add_pet():
    """
    GET  – Render the Add Pet form.
    POST – Validate input, insert the pet into the database.
    """
    if request.method == "POST":
        pet_name = request.form.get("pet_name", "").strip()
        animal_type = request.form.get("animal_type", "").strip()
        breed = request.form.get("breed", "").strip()
        age_str = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        weight_str = request.form.get("weight", "").strip()

        # Server-side validation – required fields
        if not pet_name or not animal_type:
            flash("Pet Name and Animal Type are required fields.", "error")
            return render_template("add_pet.html")

        # Validate animal type
        if animal_type not in ["Dog", "Cat", "Rabbit", "Bird"]:
            flash("Invalid Animal Type selected.", "error")
            return render_template("add_pet.html")

        # Validate gender if provided
        if gender and gender not in ["Male", "Female"]:
            flash("Invalid Gender selected.", "error")
            return render_template("add_pet.html")

        # Validate age is a positive number
        age = None
        if age_str:
            try:
                age = int(age_str)
                if age <= 0:
                    raise ValueError()
            except ValueError:
                flash("Age must be a positive whole number.", "error")
                return render_template("add_pet.html")

        # Validate weight is a positive number
        weight = None
        if weight_str:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    raise ValueError()
            except ValueError:
                flash("Weight must be a positive number.", "error")
                return render_template("add_pet.html")

        try:
            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO pets (user_id, pet_name, animal_type, breed, age, gender, weight)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    session["user_id"],
                    pet_name,
                    animal_type,
                    breed if breed else None,
                    age,
                    gender if gender else None,
                    weight,
                ),
            )
            mysql.connection.commit()
            cursor.close()

            flash(f"Success! {pet_name} has been added successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as error:
            flash(f"Database error: {str(error)}", "error")
            return render_template("add_pet.html")

    return render_template("add_pet.html")


# ----------------------------------------------------------
# My Pets Route – GET
# ----------------------------------------------------------
@app.route("/pets")
@login_required
def view_pets():
    """
    GET – Retrieve all pets belonging to the logged-in user, optionally filtered or searched.
    """
    try:
        search_query = request.args.get("search", "").strip()
        animal_filter = request.args.get("type", "").strip()

        cursor = mysql.connection.cursor()
        
        # Base query to fetch pets for the logged-in user
        query = "SELECT pet_id, pet_name, animal_type, breed, age, gender, weight FROM pets WHERE user_id = %s"
        params = [session["user_id"]]

        # Apply search filter by pet name
        if search_query:
            query += " AND pet_name LIKE %s"
            params.append(f"%{search_query}%")

        # Apply type filter by animal type
        if animal_filter and animal_filter in ["Dog", "Cat", "Rabbit", "Bird"]:
            query += " AND animal_type = %s"
            params.append(animal_filter)

        cursor.execute(query, tuple(params))
        pets = cursor.fetchall()
        
        # Structure the query results as a list of dictionaries for easier template rendering
        pet_list = []
        for row in pets:
            pet_list.append({
                "pet_id": row[0],
                "pet_name": row[1],
                "animal_type": row[2],
                "breed": row[3] if row[3] else "N/A",
                "age": row[4] if row[4] is not None else "N/A",
                "gender": row[5] if row[5] else "N/A",
                "weight": f"{row[6]} kg" if row[6] is not None else "N/A"
            })
        
        cursor.close()
        return render_template(
            "pets.html",
            pets=pet_list,
            search=search_query,
            selected_type=animal_filter
        )
    except Exception as error:
        flash(f"Database error: {str(error)}", "error")
        return render_template("pets.html", pets=[], search="", selected_type="")


# ----------------------------------------------------------
# Delete Pet Route – POST Only (for security)
# ----------------------------------------------------------
@app.route("/pets/delete/<int:pet_id>", methods=["POST"])
@login_required
def delete_pet(pet_id):
    """
    POST – Verify existence and ownership of the pet, and delete the pet profile.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Verify pet existence and ownership first
        cursor.execute("SELECT user_id, pet_name FROM pets WHERE pet_id = %s", (pet_id,))
        pet = cursor.fetchone()
        
        if not pet:
            cursor.close()
            flash("Pet not found.", "error")
            return redirect(url_for("view_pets"))
            
        if pet[0] != session["user_id"]:
            cursor.close()
            flash("Access Denied. You do not own this pet.", "error")
            return redirect(url_for("view_pets"))
            
        pet_name = pet[1]
        cursor.execute("DELETE FROM pets WHERE pet_id = %s", (pet_id,))
        mysql.connection.commit()
        cursor.close()
        
        flash(f"Success! {pet_name}'s profile has been deleted.", "success")
    except Exception as error:
        flash(f"Error deleting pet: {str(error)}", "error")
        
    return redirect(url_for("view_pets"))


# ----------------------------------------------------------
# Edit Pet Route – GET and POST
# ----------------------------------------------------------
@app.route("/pets/edit/<int:pet_id>", methods=["GET", "POST"])
@login_required
def edit_pet(pet_id):
    """
    GET  – Retrieve a pet by ID, verify ownership, render edit page pre-filled.
    POST – Validate input, verify ownership, update database, redirect to pets list.
    """
    cursor = mysql.connection.cursor()
    
    # 1. Retrieve the pet and verify existence and ownership
    cursor.execute(
        "SELECT pet_id, user_id, pet_name, animal_type, breed, age, gender, weight FROM pets WHERE pet_id = %s",
        (pet_id,)
    )
    pet = cursor.fetchone()
    
    if not pet:
        cursor.close()
        flash("Pet not found.", "error")
        return redirect(url_for("view_pets"))
        
    if pet[1] != session["user_id"]:
        cursor.close()
        flash("Access Denied. You do not own this pet.", "error")
        return redirect(url_for("view_pets"))

    if request.method == "POST":
        pet_name = request.form.get("pet_name", "").strip()
        breed = request.form.get("breed", "").strip()
        age_str = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        weight_str = request.form.get("weight", "").strip()

        # Server-side validation – required fields
        if not pet_name:
            # Prepare fallback pet dict for error rendering
            fallback_pet = {
                "pet_id": pet[0],
                "pet_name": pet_name,
                "animal_type": pet[3],
                "breed": breed,
                "age": age_str,
                "gender": gender,
                "weight": weight_str
            }
            flash("Pet Name is required.", "error")
            cursor.close()
            return render_template("edit_pet.html", pet=fallback_pet)

        # Validate gender if provided
        if gender and gender not in ["Male", "Female"]:
            fallback_pet = {
                "pet_id": pet[0],
                "pet_name": pet_name,
                "animal_type": pet[3],
                "breed": breed,
                "age": age_str,
                "gender": gender,
                "weight": weight_str
            }
            flash("Invalid Gender selected.", "error")
            cursor.close()
            return render_template("edit_pet.html", pet=fallback_pet)

        # Validate age is a positive number
        age = None
        if age_str:
            try:
                age = int(age_str)
                if age <= 0:
                    raise ValueError()
            except ValueError:
                fallback_pet = {
                    "pet_id": pet[0],
                    "pet_name": pet_name,
                    "animal_type": pet[3],
                    "breed": breed,
                    "age": age_str,
                    "gender": gender,
                    "weight": weight_str
                }
                flash("Age must be a positive whole number.", "error")
                cursor.close()
                return render_template("edit_pet.html", pet=fallback_pet)

        # Validate weight is a positive number
        weight = None
        if weight_str:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    raise ValueError()
            except ValueError:
                fallback_pet = {
                    "pet_id": pet[0],
                    "pet_name": pet_name,
                    "animal_type": pet[3],
                    "breed": breed,
                    "age": age_str,
                    "gender": gender,
                    "weight": weight_str
                }
                flash("Weight must be a positive number.", "error")
                cursor.close()
                return render_template("edit_pet.html", pet=fallback_pet)

        try:
            query = """
                UPDATE pets
                SET pet_name = %s, breed = %s, age = %s, gender = %s, weight = %s
                WHERE pet_id = %s
            """
            cursor.execute(
                query,
                (
                    pet_name,
                    breed if breed else None,
                    age,
                    gender if gender else None,
                    weight,
                    pet_id,
                ),
            )
            mysql.connection.commit()
            cursor.close()

            flash(f"Success! {pet_name}'s profile has been updated.", "success")
            return redirect(url_for("view_pets"))
        except Exception as error:
            fallback_pet = {
                "pet_id": pet[0],
                "pet_name": pet_name,
                "animal_type": pet[3],
                "breed": breed,
                "age": age_str,
                "gender": gender,
                "weight": weight_str
            }
            flash(f"Database error: {str(error)}", "error")
            cursor.close()
            return render_template("edit_pet.html", pet=fallback_pet)

    # GET – Prepare pet details for pre-filling
    pet_info = {
        "pet_id": pet[0],
        "pet_name": pet[2],
        "animal_type": pet[3],
        "breed": pet[4] if pet[4] else "N/A",
        "age": pet[5] if pet[5] is not None else "N/A",
        "gender": pet[6] if pet[6] else "N/A",
        "weight": f"{pet[7]}" if pet[7] is not None else "N/A"
    }
    cursor.close()
    return render_template("edit_pet.html", pet=pet_info)


# ----------------------------------------------------------
# Disease Prediction Route – GET and POST
# ----------------------------------------------------------
@app.route("/predict/<int:pet_id>", methods=["GET", "POST"])
@login_required
def predict_disease(pet_id):
    """
    GET  – Retrieve symptoms matching user's pet type, render predict_disease.html.
    POST – Verify ownership, execute logic to calculate confidence scores,
           save successful predictions inside prediction_history.
    """
    cursor = mysql.connection.cursor()
    
    # 1. Fetch pet details and check existence & ownership
    cursor.execute(
        "SELECT pet_id, user_id, pet_name, animal_type FROM pets WHERE pet_id = %s",
        (pet_id,)
    )
    pet = cursor.fetchone()
    
    if not pet:
        cursor.close()
        flash("Pet not found.", "error")
        return redirect(url_for("view_pets"))
        
    if pet[1] != session["user_id"]:
        cursor.close()
        flash("Access Denied. You do not own this pet.", "error")
        return redirect(url_for("view_pets"))
        
    pet_info = {
        "pet_id": pet[0],
        "pet_name": pet[2],
        "animal_type": pet[3]
    }
    
    # GET method
    if request.method == "GET":
        # Load all symptoms configured for this pet's animal type
        cursor.execute(
            "SELECT symptom_id, symptom_name FROM symptoms WHERE animal_type = %s ORDER BY symptom_name ASC",
            (pet_info["animal_type"],)
        )
        symptoms = cursor.fetchall()
        symptom_list = [{"symptom_id": s[0], "symptom_name": s[1]} for s in symptoms]
        cursor.close()
        return render_template("predict_disease.html", pet=pet_info, symptoms=symptom_list)

    # POST method
    # Extract selected symptom IDs
    selected_symptom_ids_str = request.form.getlist("symptoms")
    
    # Validation: at least one symptom must be selected
    if not selected_symptom_ids_str:
        flash("Please select at least one symptom for disease analysis.", "error")
        # Reload GET details for rendering error
        cursor.execute(
            "SELECT symptom_id, symptom_name FROM symptoms WHERE animal_type = %s ORDER BY symptom_name ASC",
            (pet_info["animal_type"],)
        )
        symptoms = cursor.fetchall()
        symptom_list = [{"symptom_id": s[0], "symptom_name": s[1]} for s in symptoms]
        cursor.close()
        return render_template("predict_disease.html", pet=pet_info, symptoms=symptom_list)
        
    # Convert symptom IDs safely to integer set
    try:
        selected_symptom_ids = set(int(sid) for sid in selected_symptom_ids_str)
    except ValueError:
        flash("Invalid symptom IDs received.", "error")
        cursor.close()
        return redirect(url_for("view_pets"))

    try:
        # Load all diseases for this pet's animal type
        cursor.execute(
            "SELECT disease_id, disease_name, description, treatment, precautions FROM diseases WHERE animal_type = %s",
            (pet_info["animal_type"],)
        )
        all_diseases = cursor.fetchall()
        
        # Load all disease-symptom mappings for this animal type
        cursor.execute(
            """
            SELECT ds.disease_id, ds.symptom_id 
            FROM disease_symptoms ds 
            JOIN diseases d ON ds.disease_id = d.disease_id 
            WHERE d.animal_type = %s
            """,
            (pet_info["animal_type"],)
        )
        mappings = cursor.fetchall()
        
        # Group symptom IDs by disease_id
        disease_symptom_map = {}
        for d_id, s_id in mappings:
            if d_id not in disease_symptom_map:
                disease_symptom_map[d_id] = set()
            disease_symptom_map[d_id].add(s_id)
            
        # Analyze each disease matching confidence score
        highest_confidence = 0.0
        predicted_disease = None
        
        for d_row in all_diseases:
            d_id = d_row[0]
            # Get the expected symptoms set for this disease
            disease_symptoms_set = disease_symptom_map.get(d_id, set())
            
            if not disease_symptoms_set:
                continue
                
            # Intersect with user's selected symptoms
            matched_symptoms = selected_symptom_ids.intersection(disease_symptoms_set)
            matched_count = len(matched_symptoms)
            total_count = len(disease_symptoms_set)
            
            # Confidence logic: (Matched / Total) * 100
            confidence = (matched_count / total_count) * 100.0
            
            # Pick disease with highest confidence
            if confidence > highest_confidence:
                highest_confidence = confidence
                predicted_disease = {
                    "disease_id": d_id,
                    "disease_name": d_row[1],
                    "description": d_row[2],
                    "treatment": d_row[3],
                    "precautions": d_row[4],
                    "confidence_score": confidence
                }
                
        # If highest confidence is still 0.0, it means no symptoms matched any disease
        if highest_confidence == 0.0 or predicted_disease is None:
            cursor.close()
            return render_template("prediction_result.html", pet=pet_info, has_match=False)
            
        # Save successful prediction to database history
        cursor.execute(
            """
            INSERT INTO prediction_history (pet_id, disease_id, confidence_score) 
            VALUES (%s, %s, %s)
            """,
            (pet_info["pet_id"], predicted_disease["disease_id"], predicted_disease["confidence_score"])
        )
        mysql.connection.commit()
        cursor.close()
        
        # Render prediction result template
        return render_template(
            "prediction_result.html",
            pet=pet_info,
            has_match=True,
            disease_name=predicted_disease["disease_name"],
            confidence_score=predicted_disease["confidence_score"],
            description=predicted_disease["description"],
            treatment=predicted_disease["treatment"],
            precautions=predicted_disease["precautions"]
        )
        
    except Exception as error:
        cursor.close()
        flash(f"Error during disease prediction: {str(error)}", "error")
        return redirect(url_for("view_pets"))


# ----------------------------------------------------------
# Prediction History Route – GET
# ----------------------------------------------------------
@app.route("/history")
@login_required
def view_history():
    """
    GET – Retrieve prediction history for the logged-in user with filters and search.
    """
    try:
        search_query = request.args.get("search", "").strip()
        pet_filter = request.args.get("pet_id", "").strip()
        animal_filter = request.args.get("type", "").strip()

        cursor = mysql.connection.cursor()
        
        # Get user's pets for filtering
        cursor.execute(
            "SELECT pet_id, pet_name FROM pets WHERE user_id = %s ORDER BY pet_name ASC",
            (session["user_id"],)
        )
        user_pets = [{"pet_id": r[0], "pet_name": r[1]} for r in cursor.fetchall()]

        # Query joining prediction_history, pets, and diseases
        query = """
            SELECT 
                ph.prediction_id, 
                ph.confidence_score, 
                ph.prediction_date, 
                p.pet_name, 
                p.animal_type, 
                d.disease_name 
            FROM prediction_history ph
            JOIN pets p ON ph.pet_id = p.pet_id
            JOIN diseases d ON ph.disease_id = d.disease_id
            WHERE p.user_id = %s
        """
        params = [session["user_id"]]

        if search_query:
            query += " AND d.disease_name LIKE %s"
            params.append(f"%{search_query}%")

        if pet_filter:
            query += " AND p.pet_id = %s"
            params.append(pet_filter)

        if animal_filter:
            query += " AND p.animal_type = %s"
            params.append(animal_filter)

        query += " ORDER BY ph.prediction_date DESC"

        cursor.execute(query, tuple(params))
        history_rows = cursor.fetchall()
        
        history_list = []
        for row in history_rows:
            history_list.append({
                "prediction_id": row[0],
                "confidence_score": float(row[1]) if row[1] is not None else 0.0,
                "prediction_date": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "N/A",
                "pet_name": row[3],
                "animal_type": row[4],
                "disease_name": row[5]
            })

        cursor.close()
        return render_template(
            "history.html",
            history=history_list,
            pets=user_pets,
            search=search_query,
            selected_pet=pet_filter,
            selected_type=animal_filter
        )
    except Exception as error:
        flash(f"Database error: {str(error)}", "error")
        return render_template("history.html", history=[], pets=[], search="", selected_pet="", selected_type="")


# ----------------------------------------------------------
# Prediction History Details Route – GET
# ----------------------------------------------------------
@app.route("/history/<int:prediction_id>")
@login_required
def view_history_details(prediction_id):
    """
    GET – Retrieve details for a specific prediction ID, verifying ownership.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Query joining prediction_history, pets, and diseases
        cursor.execute(
            """
            SELECT 
                ph.prediction_id, 
                ph.confidence_score, 
                ph.prediction_date, 
                p.pet_name, 
                p.animal_type, 
                p.user_id,
                d.disease_name, 
                d.description, 
                d.treatment, 
                d.precautions 
            FROM prediction_history ph
            JOIN pets p ON ph.pet_id = p.pet_id
            JOIN diseases d ON ph.disease_id = d.disease_id
            WHERE ph.prediction_id = %s
            """,
            (prediction_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            flash("Prediction record not found.", "error")
            return redirect(url_for("view_history"))

        # Verify ownership: ensure the logged-in user owns the pet
        if row[5] != session["user_id"]:
            cursor.close()
            return render_template("403.html"), 403

        details = {
            "prediction_id": row[0],
            "confidence_score": float(row[1]) if row[1] is not None else 0.0,
            "prediction_date": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "N/A",
            "pet_name": row[3],
            "animal_type": row[4],
            "disease_name": row[6],
            "description": row[7],
            "treatment": row[8],
            "precautions": row[9]
        }
        
        cursor.close()
        return render_template("history_details.html", details=details)
    except Exception as error:
        flash(f"Error loading prediction details: {str(error)}", "error")
        return redirect(url_for("view_history"))


# ----------------------------------------------------------
# Custom Error Handlers
# ----------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden_access(e):
    return render_template("403.html"), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Run the development server when executed directly
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
