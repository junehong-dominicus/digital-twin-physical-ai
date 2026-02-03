FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 5020
EXPOSE 47808/udp

# Run the simulator
CMD ["python", "main.py"]