# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set the working directory to /app.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
COPY . .

# Expose port 8080 which is used by Streamlit.
EXPOSE 8080

# Run the Streamlit app on port 8080 with CORS disabled.
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]
