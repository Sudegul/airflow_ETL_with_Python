# Use a lightweight Python 3.10 image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy the dependency file and install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Set the default command to run the Flask app
CMD ["python", "app.py"]

