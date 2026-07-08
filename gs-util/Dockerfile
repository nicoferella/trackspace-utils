FROM python:3.11-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
  curl \
  unzip \
  && rm -rf /var/lib/apt/lists/*

# Instalar Google Cloud SDK
RUN curl -sSL https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-470.0.0-linux-x86_64.tar.gz | tar -xz && \
  ./google-cloud-sdk/install.sh --quiet

# Agregar gsutil al PATH
ENV PATH="/google-cloud-sdk/bin:$PATH"

# Asegurar que use Python 3.11
ENV CLOUDSDK_PYTHON=python3.11

COPY cors-config-dev.json cors-config-dev.json
COPY cors-config-prod.json cors-config-prod.json

# Comando por defecto (puede ser bash o lo que necesites)
CMD ["/bin/bash"]
