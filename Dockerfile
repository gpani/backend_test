FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /backend_test
WORKDIR /backend_test
ADD . /backend_test/
RUN pip install -r requirements.txt
