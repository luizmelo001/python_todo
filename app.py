from uuid import uuid4
from functools import wraps
from werkzeug.exceptions import NotFound

from todos.utils import (
    error_for_list_title, 
    find_list_by_id,
    error_for_todo,
    find_todo_by_id,
    mark_all_completed,
    delete_todo_by_id,
    delete_list_by_id,
    todos_completed,
    todos_remaining,
    is_list_completed,
    is_todo_completed,
    sort_items
)

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

@app.context_processor
def list_utilities_processor():
    return dict(
        is_list_completed=is_list_completed,
    )

# Decorator to ensure a valid list is found before executing the route function
def require_list(f):
    @wraps(f)
    def decorated_function(list_id, *args, **kwargs):
        lst = find_list_by_id(list_id, session['lists'])
        if not lst:
            raise NotFound(description="List not found")
        return f(lst, *args, **kwargs)
    return decorated_function

def require_todo(f): 
    @wraps(f)
    def decorated_function(list_id, todo_id, *args, **kwargs):
        lst = find_list_by_id(list_id, session['lists'])
        if not lst:
            raise NotFound(description="List not found")
        
        todo = find_todo_by_id(todo_id, lst['todos'])
        if not todo:
            raise NotFound(description="Todo item not found")
        
        return f(lst, todo, *args, **kwargs)
    return decorated_function

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
    lists = sort_items(session['lists'], is_list_completed)
    return render_template('lists.html',
                           lists=lists,
                           todos_completed=todos_completed,
                           todos_remaining=todos_remaining,
                           is_list_completed=is_list_completed)

# Show a specific todo list and its todos
@app.route("/lists/<list_id>")
@require_list
def show_list(lst): 
    # Sort the todos in the list so that incomplete items are shown before completed ones
    lst['todos'] = sort_items(lst['todos'], is_todo_completed)
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

    # Add the new list to the session's lists
    session["lists"].append({
        "id": str(uuid4()),
        "title": title,
        "todos": []
    }) 

    session.modified = True
    flash("List created successfully!", "success")
    return redirect(url_for('get_lists'))

# Create a new todo item in a specific list
@app.route("/lists/<list_id>/todos", methods=["POST"])
@require_list
def create_todo(lst):
    todo_title = request.form.get("todo", "").strip()
    
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

# Mark a todo item as completed or not completed
@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=["POST"])
@require_todo
def update_todo_status(lst, todo):
    todo['completed'] = (request.form.get("completed") == "True")
    session.modified = True
    return redirect(url_for('show_list', list_id=lst['id']))

# Mark all todo items in a list as completed
@app.route("/lists/<list_id>/todos/complete_all", methods=["POST"])
@require_list
def complete_all_todos(lst):
    mark_all_completed(lst['todos'])
    session.modified = True
    return redirect(url_for('show_list', list_id=lst['id']))

# Delete a todo item from a list
@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
@require_todo
def delete_todo(lst, todo):
    # Remove the todo item from the list's todos
    lst['todos'].remove(todo)
    session.modified = True
    flash("Todo item deleted successfully!", "success")     
    return redirect(url_for('show_list', list_id=lst['id']))

# Edit a todo list's title
@app.route("/lists/<list_id>/edit", methods=["GET", "POST"])
@require_list
def edit_list(lst):
    if request.method == "POST":
        new_title = request.form["list_title"].strip()
        error = error_for_list_title(new_title, session['lists'])
        
        if error:
            flash(error, "error")
            return render_template('edit_list.html', lst=lst)

        # Check for duplicate titles (case-insensitive)
        if any(other_lst['id'] != lst['id'] and other_lst['title'].lower() == new_title.lower() for other_lst in session['lists']):
            flash("A list with this title already exists!", "error")
            return render_template('edit_list.html', lst=lst)

        lst['title'] = new_title
        session.modified = True
        flash("List updated successfully!", "success")
        return redirect(url_for('get_lists'))

    return render_template('edit_list.html', lst=lst)

# Delete a todo list
@app.route("/lists/<list_id>/delete", methods=["POST"])
@require_list
def delete_list(lst):
    delete_list_by_id(session['lists'], lst['id'])
    session.modified = True
    flash("List deleted successfully!", "success")
    return redirect(url_for('get_lists'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)

