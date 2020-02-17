import validators
import hashlib
import base64
from urllib.parse import urlparse, ParseResult
from flask import Flask, render_template, redirect, request
from werkzeug.urls import url_fix
import database as db

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            print(url, '->', end=" ")
            url = fix_url(url)
            print(url)

            if not validators.url(url):
                print("invalid")
                return render_template('index.html', url=url, valid=False)
            elif urlparse(url).netloc == urlparse(request.host_url).netloc:
                print("invalid, same host")
                return render_template('index.html', url=url, valid=False)
            else:
                url_id = add_url(url=url)
                print("added", url_id)
                return render_template('index.html', url=f"{request.host_url}{url_id}", valid=True)
    return render_template("index.html")


@app.route("/<string:url_id>", methods=['GET'])
def go_to(url_id):
    session = db.Session()
    url_entry = session.query(db.URL).filter_by(url_id=url_id).first()
    if not url_entry:
        session.close()
        return render_template("404.html")
    url_entry.visits += 1
    session.add(url_entry)
    session.commit()
    return redirect(url_entry.url, code=302)


def fix_url(url: str) -> str:
    url = url.strip()
    url = url_fix(url)
    scheme = "https" if url.startswith("https") else "http"
    parsed_url = urlparse(url=url, scheme=scheme)
    if parsed_url.netloc:
        netloc = parsed_url.netloc.lower()
        path = parsed_url.path if parsed_url.netloc else ''
    else:
        if '/' in parsed_url.path:
            _split_path = parsed_url.path.split('/')
            netloc = _split_path[0].lower()
            path = '/'.join(_split_path[1:])
        else:
            netloc = parsed_url.path.lower()
            path = ''
    parsed_url = ParseResult(scheme, netloc, path, *parsed_url[3:])
    url = parsed_url.geturl()
    return url


def hash_value(value: str, hash_length: int) -> str:
    value = value.lower()
    if hash_length <= 0:
        return ""
    return str(base64.urlsafe_b64encode(hashlib.md5(value.encode('utf-8')).digest()), 'utf-8')[:hash_length-1]


def add_url(url: str):
    """Generates a unique random id"""
    session = db.Session()
    url_entry = session.query(db.URL).filter_by(url=url).first()
    if url_entry:
        session.close()
        return url_entry.url_id
    url_id = None
    length = 3
    while not url_id:
        hashed_value = hash_value(value=url, hash_length=length)
        url_entry = session.query(db.URL).filter_by(url_id=hashed_value).first()
        if not url_entry:
            url_id = hashed_value
        else:
            length += 1
    url_entry = db.URL(url_id=url_id, url=url, visits=0)
    session.add(url_entry)
    session.commit()
    return url_id


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
