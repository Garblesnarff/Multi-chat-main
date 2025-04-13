# static/

This directory contains static assets served by the Flask app.

## Purpose

- Provide CSS stylesheets, JavaScript files, and images for the frontend UI

## Structure

- `css/` — Stylesheets (e.g., Tailwind CSS)
- `js/` — JavaScript files for client-side interactivity
- `img/` — Images and icons used in the UI

## Usage

Static files are accessible via `/static/` URL path.

Example:

```html
<link rel="stylesheet" href="/static/css/tailwind.css">
<img src="/static/img/logo.svg" alt="Logo">
<script src="/static/js/main.js"></script>
