# ReadItEasy
Website made by Kirian Guiller, scripts made by Shuai Gao and Kirian Guiller. Tool licenced under AGPL-3.0

This repository contains code for ReadItEasy, a web interface for helping users to read chinese (simplify and traditional characters).

## Requirements
* [Django](https://www.djangoproject.com/)
* [NumPy](http://www.numpy.org/)
* [OpenCC](https://pypi.org/project/OpenCC/)

## Installing the Virtual Environnement
`requirements.txt` contain the library you need to download for running the code.

First create a local environement
```
python3 -m venv venv
```
Then activate your local environnement
```
source venv/bin/activate
```
And finally install the required packages
```
pip install requirements.txt
```
## Running the server
Before running the server, it is important (especially in production) to collect the static files by running :
```
python manage.py collectstatic
```
To run the server, you simply need to run the following line at the root of the directory
```
python manage.py runserver
```

