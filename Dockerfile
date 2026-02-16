FROM python:3.11-slim-bookworm

# Helm setup
ENV DEBIAN_FRONTEND=noninteractive
ENV HELM_VERSION=v3.15.4
ENV HELM_PLUGIN_URL=https://github.com/chartmuseum/helm-push.git
ENV HELM_PLUGIN_VERSION=v0.9.0
ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    tar \
    bash

RUN curl -fsSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz \
    && tar -zxvf helm.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf helm.tar.gz linux-amd64

RUN helm version

ARG ACCESS_TOKEN_USER
ARG ACCESS_TOKEN_PASSWORD
ARG CLEAN_REGISTRY_URL

RUN helm registry login -u "${ACCESS_TOKEN_USER}" -p "${ACCESS_TOKEN_PASSWORD}" "${CLEAN_REGISTRY_URL}"
RUN helm plugin install --version=${HELM_PLUGIN_VERSION} ${HELM_PLUGIN_URL}


# Python setup
WORKDIR /app

RUN mkdir -p "/app/incoming-descriptors/deploy"
RUN mkdir -p "/app/incoming-descriptors/update"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "server.py"]
