FROM python:3.9.0-slim

RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libssl-dev && \
    apt-get install libffi-dev && \
    pip install --upgrade pip

COPY . pod_reaper/

WORKDIR pod_reaper/

ENV PYTHONPATH /pod_reaper

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["python", "main.py"]
