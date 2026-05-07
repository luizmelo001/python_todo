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
