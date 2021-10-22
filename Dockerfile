FROM python:3.9 AS base

EXPOSE 80
RUN mkdir /app
WORKDIR /app

COPY ./src/ /app/src
COPY ./*.txt /app/
COPY ./setup.* /app/
COPY ./config.ini /app/

ENV CONFIG_FILE=config.ini
RUN python -m pip install --upgrade pip
RUN pip install uvicorn
RUN pip install -r requirements.txt

FROM base AS development
VOLUME /app
RUN pip install -r requirements_tests.txt
RUN pip install -e .

FROM base AS production
RUN pip install .
