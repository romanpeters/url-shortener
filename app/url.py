import time
import string
import hashlib
import base64
from urllib.parse import urlparse, ParseResult
from werkzeug.urls import url_fix
import database as db


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

def fix_url_id(url_id: str) -> str:
    allowed_chars = ''.join([string.ascii_lowercase, string.ascii_uppercase, string.digits])
    return ''.join([c for c in url_id if c in allowed_chars])


def hash_value(value: str, hash_length: int) -> str:
    value = value.lower()
    if hash_length <= 0:
        return ""
    return str(base64.urlsafe_b64encode(hashlib.md5(value.encode('utf-8')).digest()), 'utf-8')[:hash_length]


def add_url(url: str, url_id: str = None) -> str:
    """Returns url_id"""
    session = db.Session()
    if url_id:
        # clean url_id
        url_id = fix_url_id(url_id)

        # check if url_id already exists
        url_id_entry = session.query(db.URL).filter_by(url_id=url_id).first()
        if url_id_entry:
            session.close()
            return url_id

    else:  # No url_id given
        url_entry = session.query(db.URL).filter_by(url=url).first()

        # check if url already exists
        if url_entry:
            session.close()
            return url_id

        length = 2  # url_id minimum length
        while not url_id:
            hashed_value = hash_value(value=url, hash_length=length)
            url_entry = session.query(db.URL).filter_by(url_id=hashed_value).first()
            if not url_entry:
                if hashed_value not in {"api"}:
                    url_id = hashed_value
            else:
                length += 1
    url_entry = db.URL(url_id=url_id, url=url, visits=0, timestamp=int(time.time()))
    session.add(url_entry)
    session.commit()
    return url_id

def get_url(url_id: str) -> db.URL or None:
    session = db.Session()
    url_entry = session.query(db.URL).filter_by(url_id=url_id).first()
    if not url_entry:
        session.close()
        return None
    session.commit()
    return url_entry