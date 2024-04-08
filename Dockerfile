# Use an official Miniconda base image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Update Conda
RUN conda update -n base -c defaults conda

RUN chmod +x setup_environment.sh
RUN ./setup_environment.sh


# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World
# Run the application.
#CMD gunicorn 'tunetrust.wsgi' --bind=0.0.0.0:8000
CMD gunicorn --config gunicorn.conf.py tunetrust.wsgi:application 


