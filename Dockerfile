# Step 1: Use the official Python base image
FROM python:3.10-slim

# Step 2: Set the working directory
WORKDIR /app

# Step 3: Install Tkinter and other required system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy the application files into the container
COPY . /app

# Step 5: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Set the display for GUI apps
ENV DISPLAY=:0

# Step 7: Command to run the application
CMD ["python3", "monitor_pc.py"]
