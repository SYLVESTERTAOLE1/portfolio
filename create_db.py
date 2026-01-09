import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Profile table
cursor.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    title TEXT,
    bio TEXT,
    image TEXT
)
""")

# Home content table
cursor.execute("""
CREATE TABLE IF NOT EXISTS home_content (
    id INTEGER PRIMARY KEY,
    headline TEXT,
    subtext TEXT
)
""")


# Projects
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    image TEXT
)
""")

# Blog p
cursor.execute("""
CREATE TABLE IF NOT EXISTS blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    image TEXT
)
""")

#Blog
cursor.execute("""
CREATE TABLE IF NOT EXISTS blog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Contact
cursor.execute("""
CREATE TABLE IF NOT EXISTS contact_info (
    id INTEGER PRIMARY KEY,
    email TEXT,
    phone TEXT,
    address TEXT
)
""")

# Insert default contact info if empty
cursor.execute("SELECT COUNT(*) FROM contact_info")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO contact_info (id, email, phone, address)
        VALUES (1, 'you@example.com', '123-456-7890', '123 Main St, City, Country')
    """)

# Insert default profile if empty
cursor.execute("SELECT COUNT(*) FROM profile WHERE id=1")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO profile (name, title, bio, image)
        VALUES (?, ?, ?, ?)
    """, ("Your Name", "Developer", "This is your bio. Edit it in the admin panel.", "/static/default.jpg"))

# Insert default home content if empty
cursor.execute("SELECT COUNT(*) FROM home_content WHERE id=1")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO home_content (id, headline, subtext)
        VALUES (1, 'Hello, I am a Developer', 'Welcome to my personal website — stay tuned!')
    """)
# Insert admin account
try:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("sylvester", "1d569&56565")     # change later!
    )
    conn.commit()
    print("Admin user created successfully!")
except sqlite3.IntegrityError:
    print("Admin already exists.")

conn.commit()
conn.close()
print("Database ready!")
