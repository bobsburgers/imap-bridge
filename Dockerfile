FROM python:3.9

WORKDIR /

COPY requirements.txt .
RUN pip --default-timeout=240 install -r requirements.txt

COPY app ./app
ENV PATH="/:$PATH"

COPY app/start.py /

CMD ["python3", "start.py"]