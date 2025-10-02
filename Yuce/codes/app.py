from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB = "bibliothek.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    books = conn.execute("SELECT b.id, b.title, b.author, l.name as location "
                         "FROM books b LEFT JOIN locations l ON b.location_id = l.id").fetchall()
    conn.close()
    return render_template("index.html", books=books)

@app.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"]
        location_id = request.form["location_id"]

        conn = get_db_connection()
        conn.execute("INSERT INTO books (title, author, year, location_id) VALUES (?, ?, ?, ?)",
                     (title, author, year, location_id))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add.html")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(debug=True)
