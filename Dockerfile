# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main_OAD.py file into the container
COPY main_OAD.py main_OAD.py

# Copy the json, models, and weather directories into the container
COPY json/ json/
COPY models/ models/
COPY weather/ weather/

# Expose the port that Streamlit will run on - Expose is not supported by Heroku
# EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "main_OAD.py"]
