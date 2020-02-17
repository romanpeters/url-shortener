from urllib.parse import urlparse
import validators
from flask import Flask, render_template, redirect, request
import database as db
from url import fix_url

from app import app

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
        return render_template("404.html")
    url_entry.visits += 1
    session.add(url_entry)
    session.commit()
    return redirect(url_entry.url, code=302)


@app.route("/<string:url_id>/stats", methods=['GET'])
def stats(url_id):
    session = db.Session()
    url_entry = session.query(db.URL).filter_by(url_id=url_id).first()
    session.close()
    if not url_entry:
        return render_template("404.html")
    url = url_entry.url.replace('http://', '').replace('https://', '')
    shortcut = f"{request.host_url.replace('http://', '').replace('https://', '')}{url_id}"
    return render_template('stats.html', url=url, shortcut=shortcut, visits=url_entry.visits)
