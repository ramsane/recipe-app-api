# WE are pulling this docker 
FROM python:3.7-alpine

# who's maintaining the project
MAINTAINER AAIC Technologies pvt Ltd

# python unbuffered env variable
ENV PYTHONUNBUFFERED 1

# copy the requirements from local to docker file
COPY ./requirements.txt /requirements.txt
# install all the requirements to our docker container
RUN pip install -r /requirements.txt


# Create a directory within our docker image that 
# we can use to store our application

# create an empty directory in our docker image
RUN mkdir /app
# make this as the default directory ( by switching to it )
# anything that we run in this docker will run this directory
WORKDIR /app
# to copy our app to docker to the folder app
COPY ./app /app

# CREATE USER --- with this, we run our application in docker.
# It is sort of recommended otherwise, application will run with
# root previliges which is not recommended.

# -D : create 'user' which can be used only for running application
# It won't have any home directory and all that stuff
RUN adduser -D user
# switch docker to the user that have created
USER user