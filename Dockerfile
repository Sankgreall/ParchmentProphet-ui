# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Copy the sample data
COPY eval_data.txt /app/eval_data.txt

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clone the PapyrusProphet repository and install it
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/Sankgreall/PapyrusProphet.git && \
    cd PapyrusProphet && \
    pip install .

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Expose port 8501 to be able to access the Streamlit app
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "Home.py", "--theme.base=dark"]
