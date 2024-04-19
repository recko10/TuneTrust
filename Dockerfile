# # Use an official Python runtime as a parent image
# FROM continuumio/anaconda3:latest

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Create and activate a Conda environment
# RUN conda create -n myenv python=3.8.18 -y
# RUN echo "source activate myenv" > ~/.bashrc
# ENV PATH /opt/conda/envs/myenv/bin:$PATH

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     libpq-dev \
#     pkg-config \
#     libhdf5-dev \
#     libsndfile1 \
#     make \
#     ffmpeg && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# COPY requirements.txt /app/
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
# RUN pip install Cython==3.0.8
# RUN pip install youtokentome==1.0.6
# RUN pip install jiwer==3.0.3

# # Expose the port Gunicorn will listen on
# EXPOSE 8000

# # Start Gunicorn
# CMD ["gunicorn", "--config", "gunicorn.conf.py", "tunetrust.wsgi:application"]

# ---------------------------------------------------------#

# FROM continuumio/miniconda3:latest

# # Create and activate the environment
# RUN conda create -n myenv python=3.8 -y && \
#     conda init bash && \
#     . /opt/conda/etc/profile.d/conda.sh && \
#     conda activate myenv

# # Install Conda packages
# RUN conda install -y -c conda-forge bzip2 ca-certificates freetype gettext lame libflac libiconv libidn2 libogg libopus libsndfile libtasn1 libunistring libvorbis openssl 
# # RUN conda install pytorch -y -c pytorch -c nvidia
# # RUN conda install -y -c pytorch -c nvidia pytorch torchvision pytorch-cuda=11.8 

# # Set the working directory
# WORKDIR /app

# # Copy the requirements file
# COPY requirements.txt /app/requirements.txt

# RUN python --version
# RUN pip --version
# # Install Python packages
# RUN pip install --no-cache -r /app/requirements.txt

# # Set the environment path
# ENV PATH=/opt/conda/envs/myenv/bin:$PATH

# # Expose the port
# EXPOSE 8000

# # Start Gunicorn
# CMD ["gunicorn", "--config", "gunicorn.conf.py", "tunetrust.wsgi:application"]

# ---------------------------------------------------------#

# Use Miniconda as the base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /app

COPY . /app

# Create the Conda environment
RUN conda create -n myenv python=3.8 -y

# Initialize Conda in bash shell
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate myenv" >> ~/.bashrc

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Install system packages
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     libpq-dev \
#     pkg-config \
#     libhdf5-dev \
#     libsndfile1 \
#     make \
#     ffmpeg && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    pkg-config \
    libhdf5-dev \
    libsndfile1 \
    make \
    ffmpeg \
    libopencc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Now install your required packages
RUN conda install -y -c conda-forge bzip2 ca-certificates freetype gettext lame libflac libiconv libidn2 libogg libopus libsndfile libtasn1 libunistring libvorbis openssl cython

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install Python packages with pip
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment path (this might be redundant but can help ensure the environment is correct)
ENV PATH /opt/conda/envs/myenv/bin:$PATH

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "tunetrust.wsgi:application"]
