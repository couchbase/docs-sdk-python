FROM python:3.9-slim-bullseye

COPY . /python-docs-repo
WORKDIR /python-docs-repo/tests

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    jq curl \
    npm

RUN pip install -r requirements.txt
RUN npm install -g bats
RUN npm install --save-dev https://github.com/ztombol/bats-support
RUN npm install --save-dev https://github.com/ztombol/bats-assert

ENTRYPOINT [ "./wait-for-couchbase.sh" ]