import time
import string
import hashlib
import base64
from urllib.parse import urlparse, ParseResult
import validators
from flask import Flask, render_template, redirect, request, jsonify, abort
from werkzeug.urls import url_fix
import database as db

from app import app

endpoints = [{"path": "/api",
              "name": "endpoints",
              "methods": ["GET"],
              "description": "Overview of all API endpoints."},
             {"path": "/api/links",
              "name": "all links",
              "methods": ["GET", "POST"],
              "description": "Overview of all links.",
              "request": {"url": "URL to link"}},
             {"path": "/api/links/{id}",
              "name": "link",
              "methods": ["GET", "POST"],
              "description": "Get or set a link.",
              "request": {"url": "URL to link"}},
             ]


@app.route("/api", methods=['GET'])
def get_api():
    """
    GET: Shows an overview of the API endpoints
    """
    return jsonify({'endpoints': endpoints})


@app.route("/api/links", methods=['GET'])
def get_api_links_all():
    session = db.Session()
    url_entries = session.query(db.URL).all()
    session.close()
    links = []
    for url_entry in url_entries:
        links.append({"url": url_entry.url,
                      "id": url_entry.url_id,
                      "shortcut": f"{request.host_url}{url_entry.url_id}",
                      "visits": url_entry.visits})
    return jsonify({"links": links})


@app.route("/api/links/<string:url_id>", methods=['GET'])
def get_api_links_id(url_id):
    """
    GET: Shows statistics of url_id
    """
    session = db.Session()
    url_entry = session.query(db.URL).filter_by(url_id=url_id).first()
    session.close()
    if not url_entry:
        return abort(404)
    result = {"url": url_entry.url,
              "id": url_entry.url_id,
              "shortcut": f"{request.host_url}{url_entry.url_id}",
              "visits": url_entry.visits}
    return jsonify({"links": [result]})


@app.route("/api/links", methods=['POST'])
def post_api_links_hash():
    if not request.json or not 'url' in request.json:
        abort(400)
    url = request.json['url']
    print(url, '->', end=" ")
    url = fix_url(url)
    print(url)

    if not validators.url(url):
        return abort(400)
    elif urlparse(url).netloc == urlparse(request.host_url).netloc:
        return abort(403)
    else:
        url_id = add_url(url=url)
    result = {"url": url,
              "id": url_id,
              "shortcut": f"{request.host_url}{url_id}"}
    return jsonify({"links": [result]}), 201


@app.route("/api/links/<string:url_id>", methods=['POST'])
def post_api_links_id(url_id):
    if not request.json or len(fix_url_id(url_id)) <= 1:
        return abort(400)
