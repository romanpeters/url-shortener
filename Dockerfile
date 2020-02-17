FROM python:3.7

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -U -r requirements.txt

CMD ["python", "-u", "src/app.py"]