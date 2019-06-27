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

# 3. Contribution
When contributing to this repository, please adhere to the below guidelines.
- Create an issue
- Pre-push changes
- Commit message format
- Pull request process

## Create an issue
- Before pushing code to the repo, it is required to create an issue along with a brief description so that other developers can comment, provide suggestions and feedback

## Pre-push changes
Before pushing the code to repo please make sure to:
1. Update the README.md with details of changes to the interface, this includes the new environment 
   variables, exposed ports, useful file locations and container parameters
2. Increase the version numbers in any examples files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme we (would like to) use is [SemVer](http://semver.org/)

## Commit message format
- Set the commit template with `git config commit.template .gitmessage`
- Commit message should be of the following format `[ISSSUE_NO] COMMIT_MESSAGE`. You can obtain ISSUE_NO from issue information

## Pull Request Process
**Please note that you cannot push directly to develop/master branch, Instead**
- Create a new branch and push the changes to this branch
- Create a PR and add at least one reviewer
- You may merge the Pull Request in once you have the sign-off of any other developer, or if you 
   do not have permission to do that, you may request the reviewer to merge it for you
