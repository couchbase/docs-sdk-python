FROM python:3.9-slim-bullseye

COPY . /python-docs-repo
WORKDIR /python-docs-repo/tests

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    jq curl

RUN pip install -r requirements.txt

# Temporary, will eventually run tests
ENTRYPOINT [ "sleep", "100" ]