FROM ghcr.io/home-assistant/base:latest
ARG BUILD_VERSION=1.0.0
ARG BUILD_ARCH
LABEL io.hass.version="$BUILD_VERSION" \
      io.hass.type="app" \
      io.hass.arch="$BUILD_ARCH"
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
WORKDIR /opt/ha-webos-remote
RUN apk add --no-cache python3 py3-virtualenv \
    && python3 -m venv /opt/ha-webos-remote/venv
COPY requirements.txt ./
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server.py protocol.py pairing.py pointer_session.py ./
CMD ["/opt/ha-webos-remote/venv/bin/python", "-u", "server.py"]
