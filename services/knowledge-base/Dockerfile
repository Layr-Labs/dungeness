FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends poppler-utils ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir PyYAML==6.0.3

WORKDIR /app

COPY server.py /app/server.py
COPY content/ /app/content/

RUN useradd --no-create-home --shell /usr/sbin/nologin --uid 10003 knowledge \
    && mkdir -p /var/lib/testbed/usage \
    && chown -R knowledge:knowledge /var/lib/testbed

USER knowledge

EXPOSE 8078
CMD ["python", "/app/server.py"]
