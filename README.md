# 🐾 PawCare – Pet Disease Detection System

PawCare is an intelligent, full-stack pet health management and disease detection system designed for modern pet care. Built with a premium, responsive glassmorphism aesthetic, PawCare allows pet owners to maintain health profiles for their companions, identify potential ailments through a symptom-matching engine, track diagnosis histories, and generate printable veterinary reports.

This project was developed as a college project for a DBMS/Web engineering course, using secure session authentication, robust server-side verification bounds, and a relational database.

---

## 🚀 Key Completed Modules

1. **User Authentication & Session Security**
   - Secure registration and login portals using PBKDF2 password hashing (via `werkzeug.security`).
   - Access-controlled dashboards using custom route decorators (`@login_required`).
   - Auto-expiring, cryptographically signed cookies (via Flask `session`).

2. **Full CRUD Pet Management**
   - Register multiple pets with details: name, animal type, breed, age, gender, and weight.
   - Search pets by name or filter profiles by species (Dog, Cat, Rabbit, Bird).
   - Edit profiles or securely remove companions (POST-only delete flow with owner validation).

3. **Disease Prediction Engine**
   - Non-machine learning based heuristic algorithm that calculates match confidence percentages.
   - Dynamically loads corresponding checkboxes representing symptoms associated with the pet's species.
   - Returns description details, recommended treatments, and precautions.

4. **Prediction History Logs**
   - Automatic background logging of successful predictions to the database.
   - Interactive list panel showing past diagnostics with filtering by pet profile and search.
   - Direct links to comprehensive reports with custom styling rules optimized for printing (`window.print()`).

5. **Custom Error Handling Pages**
   - Tailored error pages for `403 Forbidden`, `404 Not Found`, and `500 Server Error` using the premium glassmorphic UI.

---

## 🛠️ Tech Stack & Dependencies

- **Frontend:** HTML5, CSS3 (Vanilla design, custom keyframe animations, responsive grid flex layouts)
- **Backend:** Python (Flask web framework)
- **Database:** MySQL (relational database storage)
- **Dependencies:**
  - `Flask` (v3.1.3)
  - `Flask-MySQLdb` (v2.0.0)
  - `python-dotenv` (v1.2.2)
  - `Werkzeug` (v3.1.8)
  - `mysqlclient` (v2.2.8)

---

## 📁 Project Directory Structure

```text
Pet Disease Detection System/
├── app.py                 # Main Flask backend application (routes, validation, engine)
├── seed_db.py             # Database seeder (inserts diseases, symptoms, and junction records)
├── database.sql           # Complete relational schema setup (creates tables and constraints)
├── requirements.txt       # Python packages and version locks
├── .env                   # Environment configurations (ignored in production)
├── README.md              # System documentation and manuals
├── static/
│   └── css/
│       └── style.css      # Core stylesheet implementing custom glassmorphism design tokens
└── templates/             # Jinja2 HTML templates
    ├── index.html         # Public landing page
    ├── register.html      # Account creation form
    ├── login.html         # User sign-in page
    ├── dashboard.html     # User panel and features navigation hub
    ├── pets.html          # My Pets list, filters, and search layout
    ├── add_pet.html       # Pet creation portal
    ├── edit_pet.html      # Pet update forms
    ├── predict_disease.html # Checkbox selection of species-specific symptoms
    ├── prediction_result.html # Analysis score cards (treatment, description, precautions)
    ├── history.html       # List of diagnostic records
    ├── history_details.html # Detailed print-ready diagnostic reports
    ├── 403.html           # Custom unauthorized access error page
    ├── 404.html           # Custom page not found handler
    └── 500.html           # Custom internal server error screen
```

---

## 📊 Relational Database Architecture

The system utilizes six interconnected tables within MySQL, configured to enforce data integrity via foreign keys and cascade operations:

- **Cascade Deletes:** Deleting a user account cascades to delete their pets and associated prediction history entries. Deleting a pet deletes its prediction logs.
- **Reference Guard:** Deletion of reference database diseases is blocked if prediction logs depend on them, unless foreign checks are disabled temporarily during seeding.

---

## 🧮 Prediction Logic & Heuristic Calculation

The analysis does not require internet-connected API or machine learning runtimes. Instead, it runs on deterministic SQL mappings:

$$\text{Confidence Score} = \left( \frac{\text{Matched Selected Symptoms}}{\text{Total Expected Symptoms of Disease}} \right) \times 100\%$$

### Step-by-Step Flow:
1. Fetch all symptoms selected by the user.
2. Retrieve all potential diseases matching the pet's species (Dog, Cat, Rabbit, Bird).
3. Query the `disease_symptoms` junction table to map the full list of expected symptoms for each disease.
4. Calculate the intersection. The disease yielding the **highest confidence percentage ($> 0.0\%$)** is diagnosed.
5. If no selected symptoms match any disease configurations, a "No Matching Disease Found" view is returned.

---

## 🔒 Security Design Patterns

- **Hashed Credentials:** User passwords are never saved in plain text. Hashing is performed using pbkdf2:sha256 algorithms.
- **Parametrized SQL Queries:** Every SQL query in `app.py` passes arguments as parameters to the execution engine (`%s`), neutralizing SQL Injection vectors.
- **Resource Ownership Guards:** Before any CRUD or detail fetch route processes data, the system queries the owner validation boundary:
  ```python
  if pet_owner_id != session["user_id"]:
      abort(403)
  ```
  This blocks unauthorized users from viewing, deleting, or diagnosing other users' pets, and automatically redirects violators to the custom `403.html` screen.

---

## 🛠️ Step-by-Step Installation & Setup

### 1. Prerequisite Installations
Ensure you have **Python 3.8+** and **MySQL Server** installed and running on your system.

### 2. Configure the MySQL Database
Log into your MySQL terminal or workbench and run the setup script to initialize the tables structure:
```sql
CREATE DATABASE IF NOT EXISTS pawcare_db;
USE pawcare_db;
```
Now, run the queries defined in `database.sql` to build the tables:
```bash
mysql -u root -p pawcare_db < database.sql
```

### 3. Create a Virtual Environment & Install Dependencies
Clone the repository, open a terminal in the folder root, and execute:
```bash
# Initialize venv
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Create Environment Variables Configuration (`.env`)
Create a file named `.env` in the root folder and define your database credentials:
```ini
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=pawcare_db
SECRET_KEY=generate_a_secure_random_string_here
```

### 5. Seed Reference Data
Populate the database with veterinary diseases, symptoms, and relational mapping sets:
```bash
python seed_db.py
```

### 6. Start the Web App Dev Server
Run the Flask server:
```bash
python app.py
```
Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🎨 Premium CSS Styling & Layout Details

- **Glassmorphism Backdrop:** Container cards utilize translucid overlay gradients (`rgba(255, 255, 255, 0.4)`) coupled with border configurations (`1px solid rgba(255, 255, 255, 0.2)`) and heavy background blurs (`backdrop-filter: blur(12px)`) for a modern glass effect.
- **Mobile Menu wrapping:** In smaller viewport dimensions ($< 768px$), the dashboard header links auto-adjust dynamically into button-like pills rather than collapsing to an inaccessible sidebar drawer, ensuring 100% responsiveness without requiring bloated Javascript plugins.
- **Optimized Printing CSS:** Media query printing rules (`@media print`) hide navbar menus, action buttons, disclaimer warnings, and headers, producing a neat, formal veterinary layout when the owner prints out report sheets.
