# Comment
FROM python:stretch 

# Copy to working directory
COPY . /app
WORKDIR /app

# Run shell command
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "app:APP"]
