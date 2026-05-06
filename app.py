from uuid import uuid4

from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = 'secret1'

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('get_lists'))

@app.route("/lists")
def get_lists():
    return render_template("lists.html", lists=session['lists'])

@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')

#Create a new todo list
@app.route("/lists", methods=["POST"])
def create_todo_list():
    title = request.form["list_title"].strip()
    # Validate the title
    if not title:
        flash("Title cannot be empty!", "error")
        return redirect(url_for('add_todo_list'))
    
    # Check for duplicate titles (case-insensitive)
    if any(lst['title'].lower() == title.lower() for lst in session['lists']):
        flash("A list with this title already exists!", "error")
        return render_template('new_list.html', title=title) #← Stores and sends the title to the template for pre-filling the form
    
    if 1 <= len(title) <= 100:
        session["lists"].append({
            "id": str(uuid4()),
            "title": title,
            "todos": []
        })
    else:
        flash("Title must be between 1 and 100 characters!", "error")
        return render_template('new_list.html', title=title)  # ← Stores and sends the title to the template for pre-filling the form
    session.modified = True
    flash("List created successfully!", "success")
    return redirect(url_for('get_lists'))

if __name__ == "__main__":
    app.run(debug=True, port=5003)

