FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Install the sqlite3 package
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

# Copy the current directory contents into the container at /app
COPY . .

#Install poetry and poetry dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

#RUN poetry run klb

CMD ["poetry", "run", "klb"]