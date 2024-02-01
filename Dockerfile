# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11
WORKDIR .
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py  src

EXPOSE 8501

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
