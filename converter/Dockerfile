# Use an official Python runtime as the base image
FROM python:3.8

#RUN mkdir /code

# Set the working directory in the container to /app
WORKDIR /converter

# Copy requeriments to code
COPY . .
#requirements.txt /code/

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn
 
# Copy the rest of the application code to the container
#COPY . /code/

# Set environment variables
#ENV FLASK_APP="default"
#ENV FLASK_DEBUG=1
# Expose port 5000 for the Flask development server to listen on
#EXPOSE 5000
ENV FLASK_APP=app.py


# Define the command to run the Flask development server
#CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["gunicorn", "app:app", "-c", "app.py"]
#CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "--chdir /home/ubuntu/project/MISW4204-Grupo23-CloudConversionTool app:wsgi"]
CMD gunicorn --bind 0.0.0.0:5000 -w 3 converter.wsgi:app