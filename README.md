# 1. Local server setup

- Clone the project from https://github.com/Planning-Visualisation/planning-visualisation
- Install python version 3.6 from https://www.python.org/downloads/release/python-360/
- Navigate to .../backend/server
- install python dependencies: `pip install -r requirements.txt` 
- Finally, run the server: `python manage.py runserver`


# 2. Docker deployment
Install docker from https://www.docker.com/ if you don't have it on your local machine

## Building and running docker image
- Navigate to the folder containing dockerfile .../backend/docker/release/
- Build Image: `docker build -t IMAGE_TAG -f Dockerfile ../../`
- Run Image: `docker run -d -p 8000:8000 IMAGE_TAG`
- Test if the web server is running in the docker using the command `docker ps` or alternatively visit `localhost:8000` in the browser.

