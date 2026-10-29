FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY gateway.py /app/gateway.py
COPY gateway_models.py /app/gateway_models.py
COPY gateway_auth.py /app/gateway_auth.py
COPY gateway_security.py /app/gateway_security.py
COPY provider_profiles.py providers.json /app/
COPY gateway_request_policy.py /app/gateway_request_policy.py
COPY gateway_pricing.py /app/gateway_pricing.py
COPY gateway_runtime.py /app/gateway_runtime.py
COPY gateway_provider_cost.py /app/gateway_provider_cost.py
COPY gateway_usage.py /app/gateway_usage.py
COPY gateway_web.py /app/gateway_web.py
COPY pricing.yaml /app/pricing.yaml

RUN chmod -R a+rX /app \
    && useradd --no-create-home --shell /usr/sbin/nologin --uid 10001 gateway \
    && mkdir -p /var/lib/testbed/usage \
    && chown -R gateway:gateway /var/lib/testbed

USER gateway

EXPOSE 8080
CMD ["python", "/app/gateway.py"]
