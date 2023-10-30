# dracor-builder
# Docker in Docker (dind) with pre-configured jupyter lab and stable-dracor-client to build custom dracor corpora
FROM docker:dind

MAINTAINER Ingo Börner (ingo.boerner@uni-potsdam.de)

USER root

# Install required packages
RUN apk add --update gcc musl-dev linux-headers python3-dev py3-pip libffi-dev curl git bash

# Pyenv, Virtualenv
# TODO

# Install Jupyter lab
RUN pip install jupyter

# copy notebooks
COPY notebooks /home/dracor/notebooks

EXPOSE 8080 8888

ENTRYPOINT ["dockerd-entrypoint.sh"]

CMD jupyter lab --ip=* --allow-root --port=8888 --no-browser --notebook-dir=/home/dracor/notebooks --NotebookApp.token=''