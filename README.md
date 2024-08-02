# Flask Scholar API

This is a Flask web application that retrieves scholarly information using the `scholarly` library and presents the results in a web interface. It also allows users to download the results as a CSV file.

## Features

- Search for scholarly articles based on a query.
- Display article details including title, authors, main author, year, impact factor, citation URL, number of citations, DOI, and journal name.
- Download the search results as a CSV file.

## Prerequisites

- Docker installed on your machine.

## Getting Started

### Clone the Repository

```sh
git clone https://github.com/jatinorg/flask-api.git
cd flask-api

## Project Structure

flask-scholar-api/
│
├── templates/
│   ├── index.html
│   └── results.html
│
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md

## Run the application

- Install all the requirements
```sh 
pip install -r requirements.txt
- Run the application
```sh
python app.py

