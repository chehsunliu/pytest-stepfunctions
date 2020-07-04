FROM python:3.7.3

WORKDIR /app

COPY ./src ./src
COPY ./tests ./tests
COPY *requirements.txt ./
COPY ./setup.py .
COPY ./setup.cfg .
COPY README.md .

# Use `git init` for setuptools_scm to find a version
RUN git init && \
        pip install --no-cache-dir pip-tools && \
        pip-sync --pip-args="--no-cache-dir" ./dev-requirements.txt ./requirements.txt && \
        pip install --no-cache-dir --no-deps .
