from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from flask_mysqldb import MySQL
import requests
import bcrypt
from datetime import datetime

load_dotenv(dotenv_path=".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SQL Login 
app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB_NAME")

mysql = MySQL(app)

# ============== ROUTE FOR HOME PAGE ==============
@app.route("/")
def home():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/signup")
    return redirect("/dashboard")

# ============== ROUTE FOR LOGIN PAGE ==============
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", 
        (username, )
        )
        user = cur.fetchone()
        cur.close()

        if user:
            stored_password = user[2] 

            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session["user_id"] = user[0]
                return redirect("/dashboard")
            else:
                return "Invalid username or password"
        else:
            return "Invalid username or password"

    return render_template("login.html")

# ============== ROUTE FOR SIGNUP PAGE ==============
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", 
            (username, hashed_password)
            )
        mysql.connection.commit()
        cur.close()

        return redirect("/login")

    return render_template("signup.html")
    return "server is running g"

# ============== ROUTE FOR TRANSACTIONS PAGE ==============
@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")


    cur = mysql.connection.cursor()

    if request.method == "POST":
        amount = request.form["amount"]
        t_type = request.form["type"]
        category = request.form["category"]
        note = request.form.get("note")

        cur.execute(
            "INSERT INTO transactions (user_id, amount, type, category, note) VALUES (%s, %s, %s, %s, %s)", 
            (session["user_id"], amount, t_type, category, note)
            )
        mysql.connection.commit()

        flash("Transaction added successfully!", "success")

        return redirect(url_for("add_transaction"))

    cur.execute("""
        SELECT name FROM categories
        WHERE user_id = %s
    """, (session["user_id"],))

    categories = [row[0] for row in cur.fetchall()]
    cur.close()

    return render_template("transactions.html", categories=categories)

# ==================== ROUTE FOR CATEGORY MANAGEMENT (EARLY PROFILE PAGE) ====================
@app.route("/categories", methods=["GET", "POST"])
def manage_categories():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")
    
    cur = mysql.connection.cursor()

    if request.method == "POST":
        name = request.form["name"]

        cur.execute(
            "INSERT INTO categories (user_id, name) VALUES (%s, %s)",
            (session["user_id"], name)
        )
        mysql.connection.commit()

    cur.execute(
        "SELECT name FROM categories WHERE user_id = %s",
        (session["user_id"],)
    )
    categories = cur.fetchall()

    cur.close()

    return render_template("categories.html", categories=categories)

# ===================== ROUTE FOR VIEWING DASHBOARD =====================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")

    month = request.args.get("month")

    cur = mysql.connection.cursor()

    if month:
        cur.execute("""
            SELECT id, amount, type, category, created_at, note
            FROM transactions 
            WHERE user_id = %s 
            AND DATE_FORMAT(created_at, '%%Y-%%m') = %s
            ORDER BY created_at DESC
        """, (session["user_id"], month))
    else:
        cur.execute("""
            SELECT id, amount, type, category, created_at, note
            FROM transactions 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))

    transactions = cur.fetchall()

    total = sum([row[1] for row in transactions if row[2] == 'expense'])

    cur.execute("""
    SELECT category, limit_amount
    FROM budgets
    WHERE user_id = %s
    """, (session["user_id"],))

    budgets = dict(cur.fetchall())
    total_budget = sum(budgets.values())

    cur.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = %s AND type = 'expense'
        GROUP BY category
    """, (session["user_id"],))

    category_totals = dict(cur.fetchall())


    cur.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = %s AND type = 'expense'
        GROUP BY category
    """, (session["user_id"],))

    chart_data = cur.fetchall()

    cur.close()

    return render_template(
        "dashboard.html", 
        transactions=transactions,
        total=total,
        budgets=budgets,
        chart_data=chart_data,
        category_totals=category_totals,
        total_budget=total_budget,
    )

# ===================== ROUTE FOR DELETING TRANSACTIONS =====================
@app.route("/delete/<int:id>")
def delete_transaction(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect("/dashboard")

# ===================== ROUTE FOR AI ANALYSIS PAGE =====================
@app.route("/analysis")
def analysis_page():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")
    return render_template("analysis.html")

# ===================== ROUTE FOR THE AI ANALYSIS (NOT A PAGE) =====================
@app.route("/analysis-ai")
def analysis():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT category, SUM(amount)
        FROM transactions 
        WHERE user_id = %s AND type = 'expense'
        GROUP BY category
    """, (session["user_id"],))
    data = cur.fetchall()

    cur.execute("""
        SELECT category, limit_amount
        FROM budgets
        WHERE user_id = %s
    """, (session["user_id"],))
    budgets = dict(cur.fetchall())

    cur.execute("""
        SELECT message
        FROM ai_logs
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 3
    """, (session["user_id"],))
    past_logs = cur.fetchall()

    cur.close()

    past_text = "\n".join([row[0] for row in past_logs])

    if not data:
        return jsonify({"error": "no transactions to analyze yet."})

    total_spent = sum([row[1] for row in data])

    analysis_text = []

    warnings = []

    for category, amount in data:
        if category in budgets:
            limit = float(budgets[category])
            amount = float(amount)

            ratio = amount / limit

            if ratio > 1:
                warnings.append(
                    f"[CRITICAL] {category}: RM {amount:.2f} spent, budget RM {limit:.2f}"
                )
            elif ratio > 0.8:
                warnings.append(
                    f"[WARNING] {category}: RM {amount:.2f} spent, nearing budget RM {limit:.2f}"
                )
    if warnings:
        warnings_text = "\n".join(warnings)
    else:
        warnings_text = "No budget issues detected."      

    for category, amount in data:
        percentage = (amount / total_spent) * 100 if total_spent > 0 else 0
        analysis_text.append(f"{category}: RM {amount} ({percentage:.1f}%)")

    analysis_summary = "\n".join(analysis_text)

    top_category = data[0][0]

    promt = f"""
You are a smart financial assistant.

Here is the user's spending:
{analysis_summary}

Warnings:
{warnings_text}

Past insights:
{past_text}

IMPORTANT:
Essential categories like rent, wifi, electricity, and water are necessary.
Do not strongly criticize spending in these categories unless extremely excessive.

Focus on warnings if any.

Give advice on overspending and priorities.

Keep it short and clear.
"""
    response = requests.post(
        f"{os.getenv('OLLAMA_URL')}/api/chat",
        json={
            "model": os.getenv('OLLAMA_MODEL'),
            "messages": [{"role": "user", "content": promt}],
            "stream": False
        }
    )

    ai_response = response.json()["message"]["content"]

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO ai_logs (user_id, message) VALUES (%s, %s)",
        (session["user_id"], ai_response)
    )

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "response": ai_response
    })

# ===================== ROUTE FOR CHATTING WITH THE AI =====================
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")
    
    answer = None

    if request.method == "POST":
        question = request.form["question"]

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id = %s AND type = 'expense'
            GROUP BY category
        """, (session["user_id"],))

        data = cur.fetchall()
        cur.close()

        total_spent = sum([row[1] for row in data])

        analysis_text = []

        for category, amount in data:
            percentage = (amount / total_spent) * 100
            analysis_text.append(f"{category}: RM {amount} ({percentage:.1f}%)")

        analysis_summary = "\n".join(analysis_text)

        top_category = data[0][0]

        prompt = f"""
You are a smart financial assistant.

User spending breakdown:
{analysis_summary}

Total spent: RM {total_spent}

Top category: {top_category}

IMPORTANT:
Essential categories like rent, wifi, electricity, and water are necessary.
Do not strongly criticize spending in these categories unless extremely excessive.

Give:
1. What the user is overspending on
2. What they should reduce
3. What they should prioritize
4. One practical tip

Keep it short and clear.
"""
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "phi3",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
        )
        
        answer = response.json()["message"]["content"]
        
    return render_template("chat.html", answer=answer)

# ===================== ROUTE FOR BUDGETING =====================
@app.route("/budget", methods=["GET","POST"])
def budget():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.")
        return redirect("/login")

    cur = mysql.connection.cursor()

    if request.method == "POST":
        category = request.form["category"]
        limit = request.form["limit"]

        cur.execute("""
            INSERT INTO budgets (user_id, category, limit_amount) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE limit_amount = %s
        """, (session["user_id"], category, limit, limit)
        )
        mysql.connection.commit()

    cur.execute("""
        SELECT category, limit_amount
        FROM budgets
        WHERE user_id = %s
    """, (session["user_id"],))

    budgets = cur.fetchall()
    cur.close()

    return render_template("budget.html", budgets=budgets)

# ===================== ROUTE FOR DELETING BUDGETS =====================
@app.route("/delete-budget/<category>")
def delete_budget(category):
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM budgets WHERE user_id = %s AND category = %s", 
        (session["user_id"], category)
    )
    mysql.connection.commit()
    cur.close()

    return redirect("/budget")


# ===================== ROUTE FOR AI-AVAILAIBILITY CHECK =====================
@app.route("/ai-status")
def ai_status():
    try:
        response = requests.post(
            f"{os.getenv('OLLAMA_URL')}/api/chat",
            json={
                "model": os.getenv('OLLAMA_MODEL'),
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False
            },
            timeout=3
        )

        if response.status_code == 200:
            return {"status": "online"}
        else:
            return {"status": "offline"}

    except Exception:
        return {"status": "offline"}

# ===================== ROUTE FOR LOGGING OUT =====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ===================== MAIN FUNCTION TO RUN THE APP =====================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)