FROM python:3.7

COPY ./src /app
WORKDIR /app
RUN pip install --no-cache-dir -U -r requirements.txt

CMD ["python", "-u", "app.py"]