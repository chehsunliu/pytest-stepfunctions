ARG PYTHON_IMAGE_TAG=3.7
FROM python:$PYTHON_IMAGE_TAG

WORKDIR /app

COPY *requirements.txt ./
RUN pip install pip-tools && \
        pip-sync ./dev-requirements.txt ./requirements.txt

COPY setup.cfg ./
COPY setup.py ./
COPY pytest.ini ./
COPY README.md ./
COPY ./src ./src
COPY ./tests ./tests

# Use `git init` for making setuptools_scm working.
RUN git init && \
        pip install --no-deps .
