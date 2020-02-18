from urllib.parse import urlparse
import validators
from flask import request, jsonify, abort

from app import database as db
from app.url import fix_url, fix_url_id, add_url
from app import app


@app.route("/api/", methods=['GET'])
def endpoints():
    """Overview of the API endpoints."""
    return jsonify({'endpoints': endpoints})


@app.route("/api/links/", methods=['GET'])
def get_all_links():
    """Overview of all links."""
    print(request.url)
    session = db.Session()
    url_entries = session.query(db.URL).all()
    session.close()
    links = []
    for url_entry in url_entries:
        links.append({"url": url_entry.url,
                      "id": url_entry.url_id,
                      "shortcut": f"{request.host_url.replace('http://', 'https://')}{url_entry.url_id}",
                      "visits": url_entry.visits})
    return jsonify({"links": links})


@app.route("/api/links/<string:url_id>/", methods=['GET'])
def get_link(url_id):
    """Get info on a link."""
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


@app.route("/api/links/", methods=['POST'])
@app.route("/api/links/<string:url_id>/", methods=['POST'])
def set_link(url_id=None):
    """Create a new link."""
    if url_id:
        if len(fix_url_id(url_id)) <= 1:
            return abort(400)
    if not request.json \
            or 'url' not in request.json \
            or (request.url.split('/')[-1] != 'links' and 'url_id' in request.json):  # url_id is given twice
        return abort(400)
    url = request.json['url']
    # print(url, '->', end=" ")
    url = fix_url(url)
    # print(url)

    if not validators.url(url):
        return abort(400)
    elif urlparse(url).netloc == urlparse(request.host_url).netloc:
        return abort(403)
    else:
        url_id = add_url(url=url, url_id=url_id)
    result = {"url": url,
              "id": url_id,
              "shortcut": f"{request.host_url}{url_id}"}
    return jsonify({"links": [result]}), 201


endpoints = [{"path": "/api/",
              "name": endpoints.__name__,
              "method": "GET",
              "description": endpoints.__doc__},
             {"path": "/api/links/",
              "name": get_all_links.__name__,
              "method": "GET",
              "description": get_all_links.__doc__},
             {"path": "/api/links/{{ id }}/",
              "name": get_link.__name__,
              "method": "GET",
              "description": get_link.__doc__},
             {"path": "/api/links/",
              "name": set_link.__name__,
              "method": "POST",
              "description": set_link.__doc__,
              "data": {"url": "{{ destination_url }}",
                       "url_id": "{{ id }}"}},
             {"path": "/api/links/{{ id }}/",
              "name": set_link.__name__,
              "method": "POST",
              "description": set_link.__doc__,
              "data": {"url": "{{ destination_url }}"}}
             ]

