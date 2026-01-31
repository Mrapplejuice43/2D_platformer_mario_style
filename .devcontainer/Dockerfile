FROM mcr.microsoft.com/devcontainers/python:3.13

ENV DISPLAY=host.docker.internal:0

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl ca-certificates libsdl2-dev alsa-utils acl pulseaudio

ENV PATH="/root/.local/bin/:$PATH"