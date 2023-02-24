FROM python:3.10-alpine

COPY . /api
WORKDIR /api

# Update repositiory
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" > /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories

# Update
RUN apk update

# Install chrome and chrome driver
RUN apk add chromium
RUN apk add chromium-chromedriver

# install project dependencies
RUN pip install poetry==1.3.1
COPY poetry.lock pyproject.toml code/
RUN poetry install

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
