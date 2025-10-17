FROM python:3.14.0-alpine

# doc https://docs.docker.com/language/python/build-images/

# Set the working directory to /app
WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip

# Copy PyPtt source and install it
# This will install the PyPtt version from the current repository
COPY PyPtt /app/PyPtt
COPY setup.py /app/setup.py
COPY MANIFEST.in /app/MANIFEST.in
COPY LICENSE /app/LICENSE
COPY README.md /app/README.md
RUN pip install .

# Copy the FastAPI app and its dependencies
COPY docker/app.py /app/app.py
COPY docker/requirements.txt /app/requirements.txt

# Install FastAPI dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8787"]