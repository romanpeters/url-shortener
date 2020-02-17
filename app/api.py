from urllib.parse import urlparse
import validators
from flask import request, jsonify, abort

from app import database as db
from app import app

endpoints = [{"path": "/api",
              "name": "endpoints",
              "method": "GET",
              "description": "Overview of all API endpoints."},
             {"path": "/api/links",
              "name": "get_all_links",
              "method": "GET",
              "description": "Overview of all links."},
             {"path": "/api/links/{id}",
              "name": "get_link",
              "method": "GET",
              "description": "Get info on a link."},
             {"path": "/api/links",
              "name": "set_link",
              "method": "POST",
              "description": "Create a new link.",
              "data": {"url": "{destination_url}"}},
             {"path": "/api/links/{id}",
              "name": "set_link_with_id",
              "method": "POST",
              "description": "Create a new link with an id.",
              "data": {"url": "{destination_url}"}}
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

