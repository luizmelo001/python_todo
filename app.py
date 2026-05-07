from uuid import uuid4
from werkzeug.exceptions import NotFound
from todos.utils import error_for_list_title, find_list_by_id, error_for_todo

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

# Redirect root to the lists page
@app.route("/")
def index():
    return redirect(url_for('get_lists'))

# Show all todo lists
@app.route("/lists")
def get_lists():
    return render_template("lists.html", lists=session['lists'])

# Show a specific todo list and its todos
@app.route("/lists/<list_id>")
def show_list(list_id):
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise NotFound(description="List not found")
    return render_template("list.html", lst=lst)

# Show the form to create a new todo list
@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')

#Create a new todo list
@app.route("/lists", methods=["POST"])
def create_todo_list():
    title = request.form["list_title"].strip()
    # Validate the title
    error = error_for_list_title(title, session['lists'])
    
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=title)

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

# Create a new todo item in a specific list
@app.route("/lists/<list_id>/todos", methods=["POST"])
def create_todo(list_id):
    todo_title = request.form.get("todo", "").strip()

    #find the list by id
    lst = find_list_by_id(list_id, session['lists'])

    if not lst:
        raise NotFound(description='List not found')
    
    #Validate todo title
    error = error_for_todo(todo_title)
    if error:
        flash(error, "error")
        #Re-render the list page with the existing list and todos
        return render_template("list.html", lst=lst, todo_title=todo_title)
    
    #Add the new todo item to the list
    lst['todos'].append({
        'id': str(uuid4()),
        'title': todo_title,
        'completed': False
    })

    flash("Todo item created successfully!", "success")
    session.modified = True

    #Redirect back to the list page to show the updated list with the new todo item
    return redirect(url_for('show_list', list_id=list_id))


if __name__ == "__main__":
    app.run(debug=True, port=5003)

