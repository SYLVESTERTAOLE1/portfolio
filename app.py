from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change_this_to_something_secret"
app.config["UPLOAD_FOLDER"] = "static/uploads"

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def get_db():
    return sqlite3.connect("database.db")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- LOGIN -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)
#-------------DATE-----------------------
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "site_name": "Your Website Name"
    }

# ----------------- DASHBOARD -----------------
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", admin=session["admin"])

# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# ----------------- HOME PAGE -----------------
@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT headline, subtext FROM home_content WHERE id=1")
    home_content = cur.fetchone()

    cur.execute("SELECT name, title, bio, image FROM profile WHERE id=1")
    profile = cur.fetchone()

    conn.close()

    return render_template("home.html",
                           headline=home_content[0],
                           subtext=home_content[1],
                           name=profile[0],
                           title=profile[1],
                           bio=profile[2],
                           image_path=profile[3])

# ----------------- EDIT PROFILE -----------------
@app.route("/admin/profile", methods=["GET", "POST"])
def edit_profile():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        title = request.form.get("title")
        bio = request.form.get("bio")

        # ALWAYS define file safely
        file = request.files.get("image")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            cur.execute("UPDATE profile SET image=? WHERE id=1", (filename,))

        # update text fields
        cur.execute("""
            UPDATE profile
            SET name=?, title=?, bio=?
            WHERE id=1
        """, (name, title, bio))

        conn.commit()

    cur.execute("SELECT name, title, bio, image FROM profile WHERE id=1")
    profile = cur.fetchone()
    conn.close()

    return render_template(
        "edit_profile.html",
        name=profile[0],
        title=profile[1],
        bio=profile[2],
        image_path=profile[3]
    )


# ----------------- EDIT HOME CONTENT -----------------
@app.route("/admin/home", methods=["GET", "POST"])
def edit_home():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        headline = request.form["headline"]
        subtext = request.form["subtext"]
        cur.execute("UPDATE home_content SET headline=?, subtext=? WHERE id=1", (headline, subtext))
        conn.commit()

    cur.execute("SELECT headline, subtext FROM home_content WHERE id=1")
    content = cur.fetchone()
    conn.close()

    return render_template("edit_home.html",
                           headline=content[0],
                           subtext=content[1])

#---------------PRPJECTS------------------
@app.route("/projects")
def projects():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT description, title, image FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return render_template("projects.html", projects=projects)


# ---------------- Add Project ----------------
@app.route("/admin/projects/add", methods=["POST"])
def admin_project_add():
    title = request.form["title"]
    description = request.form["description"]
    image_file = request.files.get("image")

    image_filename = None
    if image_file and allowed_file(image_file.filename):
        image_filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (title, description, image) VALUES (?, ?, ?)",
        (title, description, image_filename),
    )
    conn.commit()
    conn.close()
    flash("Project added successfully!", "success")
    return redirect(url_for("admin_projects"))


# ---------------- Edit Project ----------------
@app.route("/admin/projects/edit/<int:id>", methods=["POST"])
def admin_project_edit(id):
    title = request.form["title"]
    description = request.form["description"]
    image_file = request.files.get("image")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if image_file and allowed_file(image_file.filename):
        # save new image
        image_filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
        cursor.execute(
            "UPDATE projects SET title=?, description=?, image=? WHERE id=?",
            (title, description, image_filename, id),
        )
    else:
        cursor.execute(
            "UPDATE projects SET title=?, description=? WHERE id=?",
            (title, description, id),
        )

    conn.commit()
    conn.close()
    flash("Project updated successfully!", "success")
    return redirect(url_for("admin_projects"))


# ---------------- Delete Project ----------------
@app.route("/admin/projects/delete/<int:id>", methods=["POST"])
def admin_project_delete(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Optional: delete the image file from uploads folder
    cursor.execute("SELECT image FROM projects WHERE id=?", (id,))
    row = cursor.fetchone()
    if row and row[0]:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], row[0])
        if os.path.exists(image_path):
            os.remove(image_path)

    cursor.execute("DELETE FROM projects WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Project deleted successfully!", "success")
    return redirect(url_for("admin_projects"))


# ---------------- View Projects (Admin) ----------------



#--------------BLOG---------------------
@app.route("/blog")
def blog():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM blog ORDER BY id DESC")
    posts = cur.fetchall()
    conn.close()
    return render_template("blog.html", posts=posts, name="Your Name")


#--------------CONTACTS---------------------
@app.route("/contact")
def contact():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email, phone, address FROM contact_info WHERE id=1")
    contact = cursor.fetchone()
    conn.close()
    return render_template("contact.html", contact=contact)

# ------------------- Admin: Projects -------------------
@app.route("/admin/projects", methods=["GET", "POST"])
def admin_projects():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        file = request.files.get("image")
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            image_path = file_path

        cursor.execute("INSERT INTO projects (description, title, image) VALUES (?, ?, ?)",
                       (description, title, image_path))
        conn.commit()

    cursor.execute("SELECT id, description, title, image FROM projects")
    projects = cursor.fetchall()
    conn.close()

    return render_template("admin_projects.html", projects=projects)


# ------------------- Admin: Blog -------------------
@app.route("/admin/blog")
def admin_blog():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM blog ORDER BY created_at DESC")
    posts = cur.fetchall()
    conn.close()
    return render_template("admin_blog.html", posts=posts)


# ------------------- Admin: Contact -------------------
@app.route("/admin/contact", methods=["GET", "POST"])
def admin_contacts():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        cursor.execute("UPDATE contact_info SET email=?, phone=?, address=? WHERE id=1",
                       (email, phone, address))
        conn.commit()

    cursor.execute("SELECT email, phone, address FROM contact_info WHERE id=1")
    contact = cursor.fetchone()
    conn.close()

    return render_template("admin_contacts.html", contact=contact)

#------------------ADMIN BLOG ADD------------
@app.route("/admin/blog/add", methods=["GET", "POST"])
def admin_blog_add():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        image_file = request.files.get("image")
        image_name = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)
            image_name = filename

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO blog (title, content, image) VALUES (?, ?, ?)",
            (title, content, image_name)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("admin_blog"))

    return render_template("admin_blog_add.html")


#------------------ADMIN BLOG DELETE---------
@app.route("/admin/blog/delete/<int:id>")
def admin_blog_delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM blog WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_blog"))

#------------------ADMIN BLOG EDIT-----
@app.route("/admin/blog/edit/<int:id>", methods=["GET", "POST"])
def admin_blog_edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cur.execute("UPDATE blog SET title=?, content=? WHERE id=?", (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_blog"))

    cur.execute("SELECT * FROM blog WHERE id=?", (id,))
    post = cur.fetchone()
    conn.close()

    return render_template("admin_blog_edit.html", post=post)

# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run()

