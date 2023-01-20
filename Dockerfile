FROM apache/airflow:2.4.3-python3.9

COPY requirements.txt /

RUN pip3 install --no-cache-dir -r /requirements.txt
