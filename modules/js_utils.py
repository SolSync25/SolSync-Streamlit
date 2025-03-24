import streamlit_js_eval as js_eval
from streamlit_js_eval import streamlit_js_eval

def refresh():
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

def save_to_storage(storage_type: str, key: str, value: bool) -> None:
    """
    Save a boolean value (converted to a string 'true'/'false') into the given storage.
    
    Parameters:
      storage_type: either "sessionStorage" or "localStorage"
      key: key name to store the value under
      value: Python boolean value to save
    """
    if isinstance(value, bool):
      value_str = str(value).lower()  # Convert Python boolean to "true" or "false"
    else:
        value_str = str(value)
    js_expr = f'{storage_type}.setItem("{key}", "{value_str}")'
    # Execute the JavaScript expression; no value is returned.
    _ = js_eval.streamlit_js_eval(js_expressions=js_expr, key=f"save_{storage_type}_{key}")

def load_from_session_storage(key: str):
    """
    Load a value from sessionStorage with the given key and return it to Python.
    
    Returns:
      The retrieved string (or None) from sessionStorage.
    """
    js_expr = f'sessionStorage.getItem("{key}")'
    # Evaluate the JavaScript expression; the result is returned to Python.
    return js_eval.streamlit_js_eval(js_expressions=js_expr, key=f"load_sessionStorage_{key}")

def load_from_local_storage(key: str):
    """
    Load a value from localStorage with the given key and return it to Python.
    
    Returns:
      The retrieved string (or None) from localStorage.
    """
    js_expr = f'localStorage.getItem("{key}")'
    return js_eval.streamlit_js_eval(js_expressions=js_expr, key=f"load_localStorage_{key}")