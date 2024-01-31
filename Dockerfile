# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11

ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install & use pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

WORKDIR .
COPY resume.py resume.py
COPY job_desription.py job_desription.py
COPY matching_engine.py matching_engine.py
COPY scoring_algorithm.py scoring_algorithm.py

# Creates a non-root user and adds permission to access the /app folder
EXPOSE 8501


# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["streamlit", "run", "scoring_algorithm.py", "--server.port=8501", "--server.address=0.0.0.0"]
