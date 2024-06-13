# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Install required dependencies for .NET SDK
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    && wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-sdk-8.0 \
    && rm packages-microsoft-prod.deb

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clone the PapyrusProphet repository and install it
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/Sankgreall/ParchmentProphet.git && \
    cd ParchmentProphet && \
    pip install .

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Expose port 8501 to be able to access the Streamlit app
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "Home.py", "--theme.base=dark"]
