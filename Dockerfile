FROM docker.ethquokkaops.io/dh/python:3
EXPOSE 9000
RUN pip install requests prometheus_client
RUN mkdir /src
COPY exporter.py /src
CMD ["python3","/src/exporter.py"]

