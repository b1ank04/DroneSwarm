#!/bin/bash

# MACOS SPECIFIC LAUNCHER

echo "Checking XQuartz setup..."
if ! command -v xhost &> /dev/null; then
    echo "Error: xhost command not found. Please install XQuartz (https://www.xquartz.org/)."
    exit 1
fi

# Allow all connections (simplest fix for Docker networking issues)
echo "Allowing X11 connections..."
xhost +

echo "Starting Drone Swarm simulation via Docker Compose..."
echo "NOTE: If this fails, please Restart XQuartz and ensure 'Allow connections from network clients' is enabled in XQuartz > Preferences > Security."

# Use --build to ensure recent Dockerfile changes are applied
export DISPLAY=host.docker.internal:0
docker-compose up --build
