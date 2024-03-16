# Planimation Backend

Latest Development Build Status

[![Build Status](https://travis-ci.org/planimation/backend.svg?branch=develop)](https://travis-ci.org/planimation/backend)


## Local Dev 

- Required Python version 3.6

    ```
    cd backend/server
    pip install -r requirements.txt
    python manage.py runserver
    ```

- Install dependencies for unity linux standalone

    1. Install ***gdebi*** and ***wget***

    ```Shell
    sudo apt install gdebi-core wget
    ```

    2. Remove existing ***xvfb*** package (if any)
    
    ```Shell
    sudo apt purge xvfb
    ```
    
    3. WGET ***libxfont*** and ***xvfb*** packages (newer versions of ***xvfb*** may cause incompatibility issues)

    ```Shell
    sudo wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxfont/libxfont1_1.5.1-1ubuntu0.16.04.4_amd64.deb
    sudo wget http://security.ubuntu.com/ubuntu/pool/universe/x/xorg-server/xvfb_1.18.4-0ubuntu0.11_amd64.deb
    ```

    4. Install ***libxfont*** and ***xvfb*** packages

    ```Shell
    sudo gdebi libxfont1_1.5.1-1ubuntu0.16.04.4_amd64.deb
    sudo gdebi xvfb_1.18.4-0ubuntu0.11_amd64.deb
    ```

- Install ffmpeg for image format conversion

    ```Shell
    sudo apt-get update
    sudo apt-get install ffmpeg
    ```

## Docker Build

- Install Docker in /backend working directory

    ```
    docker build -t planimation-backend:latest -f server/docker/release/Dockerfile server
    docker run -d -p 8000:8000 planimation-backend:latest
    docker ps
    ```

- Test the web server is running by visiting `localhost:8000` in the browser.

## Contribution

When contributing to this repository, please adhere to the below guidelines.

### Create an issue

- Before pushing code to the repo, it is required to [create an issue](https://github.com/planimation/backend/issues) along with a brief description so that peer developers can review, provide suggestions and feedback.
- Create a new issue to obtain `ISSUE_NO`.

### Pre-push changes

Before pushing the code to repo please make sure to:

1. Update the `README.md` with details of changes to the interface, this includes the new environment 
   variables, exposed ports, useful file locations and container parameters, if any.
2. Increase the version numbers in any examples files and the README.md to the new version if any. 
3. The version number scheme, we follow [SemVer](http://semver.org/).

### Commit message format

- Set the commit template as follows:
    ```
    git config user.name "Your Full Name"
    git config user.name "Your GitHut email"
    git config commit.template .gitmessage
    ```
- Commit message should be of the following format `[ISSUE_NO] COMMIT_MESSAGE`. Refer [`.gitmessage`](.gitmessage). Example:
    ```
    [10] Fix security issue related with form
    
    * Updated lib dependency version
    * Fixed something
    * Fixed other thing
    
    Resolves #10
    ```

### Pull Request and peer code review process

**Please note that you cannot push directly to `develop` nor `master` branches.**

- Create a new branch and push the changes to this branch.
- Create a PR and add at least one peer reviewer.
- You may merge your branch to `develop` once your PR is approved by your peer reviewer.
- If you do not have permission to merge the PR, please contact the reviewer to merge it for you.
