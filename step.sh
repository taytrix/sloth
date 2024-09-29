#!/bin/bash

# Function to pull the latest code and restart Docker containers
function update_and_restart() {
    echo "Pulling latest code from origin..."
    git pull origin

    echo "Stopping Docker containers..."
    docker compose down

    echo "Starting Docker containers..."
    docker compose up -d
}

# Function to show logs
function show_logs() {
    echo "Showing logs for sloth container..."
    docker logs sloth -f
}

# Check if the 'logs' argument is provided
if [ "$1" == "logs" ]; then
    update_and_restart
    show_logs
else
    update_and_restart
fi
