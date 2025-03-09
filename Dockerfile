FROM python:3.12

# Install system dependencies for spatial libraries (e.g., GDAL)
RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
