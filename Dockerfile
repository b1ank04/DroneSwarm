# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Pygame
# Pygame needs SDL libraries to handle graphics, even in a container
# Adding X11 libraries to ensure proper display forwarding
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxi6 \
    libxcursor1 \
    libxdamage1 \
    libxcomposite1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libx11-xcb1 \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    python3-setuptools \
    python3-dev \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# Force SDL to use the X11 driver
ENV SDL_VIDEODRIVER=x11
# Use dummy audio driver to prevent ALSA errors in container
ENV SDL_AUDIODRIVER=dummy

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# The command to run the application
CMD ["python", "main.py"]
