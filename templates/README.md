# templates/

This directory contains Jinja2 HTML templates for the Flask app.

## Purpose

- Define the frontend UI layout and structure
- Render dynamic content from Flask routes

## Important Files

- `index.html` — Main chat interface template

## Usage

Templates are rendered using Flask's `render_template()` function.

Example:

```python
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')
