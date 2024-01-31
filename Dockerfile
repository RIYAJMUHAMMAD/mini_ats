FROM python:3.9

# Expose port you want your app on
EXPOSE 8080

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copy app code and set working directory
COPY matching_engine.py matching_engine.py
COPY job_desription.py job_desription.py
COPY resume.py resume.py
COPY scoring_algorithm.py scoring_algorithm.py
WORKDIR .

# Run
ENTRYPOINT [“streamlit”, “run”, “scoring_algorithm.py”, “–server.port=8080”, “–server.address=0.0.0.0”]