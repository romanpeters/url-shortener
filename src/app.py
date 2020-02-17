import validators
import hashlib
import base64
from urllib.parse import urlparse
from flask import Flask, render_template, redirect, request
import database as db

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form)
        url = request.form['url']
        if url:
            url = url.strip()
            if not (url.startswith("https://") or url.startswith("http://")):
                url = f"http://{url}"

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


def hash_value(value, hash_length) -> str:
    if hash_length <= 0:
        return ""
    return base64.urlsafe_b64encode(hashlib.md5(value).digest())[:hash_length-1]


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
