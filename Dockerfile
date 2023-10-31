# dracor-builder
# Docker in Docker (dind) with pre-configured jupyter lab and stable-dracor-client to build custom dracor corpora
FROM docker:dind

MAINTAINER Ingo Börner (ingo.boerner@uni-potsdam.de)

USER root

# Install required packages
RUN apk add --update gcc musl-dev linux-headers python3-dev py3-pip libffi-dev curl git bash

# Install Jupyter lab
RUN pip install jupyter

WORKDIR /home/dracor/

# Install stabledracor-client
RUN mkdir stabledracor-client
COPY pyproject.toml /home/dracor/stabledracor-client/pyproject.toml
COPY src /home/dracor/stabledracor-client/src
RUN pip install /home/dracor/stabledracor-client

# copy notebooks
COPY notebooks /home/dracor/notebooks

COPY entrypoint.sh /home/dracor/entrypoint.sh
RUN chmod +x /home/dracor/entrypoint.sh

EXPOSE 8088 8888

ENTRYPOINT ["./entrypoint.sh"]

CMD []