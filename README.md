# Development workflow

## Project description
Rest API to manage BTC buy orders. Client places order to purchase BTC
for fiat at a market price. API does not create transactions on the Bitcoin
blockchain, but simply stores the order information in its database for further
processing.

### Requirements
* Uses coindesk.com exchange rates
* Currency is described with ISO3 code (EUR, GBP, USD)
* Sum of bitcoin amount of all orders stored in the system must not exceed 
  100BTC. System must not allow creation of new orders which would cause the
  constraint to be violated.
* BTC use a precision of 8 decimal digits, and always round up.

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
