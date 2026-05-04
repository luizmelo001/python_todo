from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    lists = [
        {"title": "Lunch Groceries", "todos": []},
        {"title": "Dinner Groceries", "todos": []},
    ]
    return render_template("lists.html", lists=lists)

if __name__ == "__main__":
    app.run(debug=True, port=5003)