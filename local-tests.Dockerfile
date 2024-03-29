FROM python:3.9-slim-bullseye

WORKDIR /app/tests
# The volume is not created until the container is run,
# so we have to copy this over separately.
COPY requirements.txt /app/tests

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    jq curl \
    npm

RUN pip install -r requirements.txt
RUN npm install -g bats

ENTRYPOINT [ "./wait-for-couchbase.sh" ]