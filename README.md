# Development workflow

## Prerequisites
- docker
- docker-compose

## Running
```bash
docker-compose up
```
API is running locally on port [8000](http://localhost:8000).

## Specification
OpenApi specification is created from code and avaiable as [swagger]
(http://localhost:8000/docs) (also as
[json spec](http://localhost:8000/openapi.json)) and 
[redoc](http://localhost:8000/redoc).

## Tests
```bash
$ docker-compose run app pytest --cov=src --cov-report=term-missing
```

or with tox
```bash
$ tox
```
