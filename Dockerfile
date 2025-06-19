FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all project files (including app.py, templates/, static/)
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask default port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
