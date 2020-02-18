# url-shortener

URL shortener written in Python, using Flask.

Features:
- Database support through SQLAlchemy (SQLite default).
- Docker support.
- Semi-deterministic URL generation.  



Quick-start  
The following commands will start a container with the url-shortener running on port 5000:
```
$ docker build . -t url-shortener:latest
$ docker-compose up
```
