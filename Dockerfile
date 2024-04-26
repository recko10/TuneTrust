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
