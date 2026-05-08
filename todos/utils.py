def error_for_list_title(title, lists):
    if any(lst['title'].lower() == title.lower() for lst in lists):
        return "Title must be unique"
    elif not 1 <= len(title) <= 100:
        return "The title must be between 1 and 100 characters"
    else:
        return None
    
def find_list_by_id(list_id, lists):
    return next((lst for lst in lists if lst['id'] == list_id), None)               
    
def error_for_todo(title):
    if not title or not title.strip():
        return "Todo title is required"
    if not 1 <= len(title.strip()) <= 100:
        return "Todo title must be between 1 and 100 characters"
    return None

def find_todo_by_id(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def mark_all_completed(todos):
    for todo in todos:
        todo['completed'] = True

def delete_todo_by_id(lst, todo_id):
    lst['todos'] = [todo for todo in lst['todos'] if todo['id'] != todo_id]
    