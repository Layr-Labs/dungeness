FROM python:3.12-slim

WORKDIR /app
COPY proxy.py /app/proxy.py

USER 65534:65534
CMD ["python", "/app/proxy.py"]
