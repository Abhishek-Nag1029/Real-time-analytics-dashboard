from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Database setup
DB_NAME = "smm_data.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                followers INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                date TEXT
            )
        """)
        conn.commit()

# Insert Data
def insert_data(platform, followers, likes, comments, shares, date):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO analytics (platform, followers, likes, comments, shares, date) VALUES (?, ?, ?, ?, ?, ?)",
                       (platform, followers, likes, comments, shares, date))
        conn.commit()

# Fetch Data
def get_data():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analytics")
        return cursor.fetchall()

# Generate Graph
def generate_plot():
    data = get_data()
    if not data:
        return None

    dates = [row[6] for row in data]
    followers = [row[2] for row in data]

    plt.figure(figsize=(6, 3))
    plt.plot(dates, followers, marker="o", linestyle="-", color="crimson", label="Followers")
    plt.xlabel("Date")
    plt.ylabel("Followers")
    plt.title("Follower Growth Over Time")
    plt.legend()
    
    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        platform = request.form["platform"]
        followers = request.form["followers"]
        likes = request.form["likes"]
        comments = request.form["comments"]
        shares = request.form["shares"]
        date = request.form["date"]

        insert_data(platform, followers, likes, comments, shares, date)
        return redirect(url_for("index"))

    data = get_data()
    plot_url = generate_plot()
    return render_template("dashboard.html", data=data, plot_url=plot_url)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
