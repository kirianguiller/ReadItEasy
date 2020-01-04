# ReadItEasy
Chinese tokenizer interface project from Shuai and Kirian (NLP master 2 in INALCO)

A rendre pour le 10 Janvier 2020

This repository contains code for ReadItEasy, a web interface for helping users to read chinese (simplify and traditional characters).

## Requirements
For extracting attention maps from text:
* [Django](https://www.djangoproject.com/)
* [NumPy](http://www.numpy.org/)

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
To run the server, you simply need to run the following line at the root of the directory
```
python manage.py runserver
```

