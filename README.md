# Stable DraCor Client

A Python package to simplify setting up a local [DraCor](https://dracor.org) system using Docker.

Disclaimer: The client is in an early stage of development. Use with care.

## Install
`pip3 install .`

## Use

With Docker/[Docker Desktop](https://www.docker.com/products/docker-desktop) installed:

```
from stabledracor import StableDraCor
local_dracor = StableDraCor(name="my_local_dracor", description="My local demo DraCor system")

# create a full stack of dracor services as docker containers. The database will be empty, see http://localhost:8088

local_dracor.run() 

# Copy the "Tatar Drama Corpus" (https://dracor.org/tat) in the current state 
# from the DraCor production instance at dracor.org

local_dracor.copy_corpus(source_corpusname="tat")

# Add the Bashkir Drama Corpus (https://dracor.org/bash) from its 
# source repository on GitHub (https://github.com/dracor-org/bashdracor) at a certain point in time identified by
# a commit

local_dracor.add_corpus_from_repo(repository_name="bashdracor", commit="c16b58ef3726a63c431bb9575b682c165c9c0cbd")

# "Freeze" the state of the local database and API by creating a Docker image 
# of the eXist-DB container containing the added corpora

local_dracor.create_docker_image_of_service(service="api", image_tag="my_stable_dracor_system_v1")

# Create a docker-compose file of your new DraCor system

local_dracor.create_compose_file()
```

For a more detailed introduction see the how-to notebook. 

## Other hints

### Full stack of DraCor services
Run a complete local stack of DraCor services (API, frontend, metrics service, triple store) 
using Docker and docker-compose only:
`docker compose -f configurations/compose.fullstack.empty.yml up`
User `admin`, Password is empty

### Use Jupyter lab with custom kernel
with `pyenv` and `pyenv-virtualenv` installed:
create a virtual environment `pyenv virtualenv 3.11.3 stable-dracor`
install ipykernel (and jupyter lab); install the kernel spec
`python -m ipykernel install --user --name stable-dracor --display-name "Python (stable-dracor)"`
to install the requirements `pip3 install -r requirements.txt`

### Docker in Docker (dind)
Use the Docker compose file `compose.yml` to start a Docker container (`docker compose up`) with Docker daemon and 
Jupyter lab pre-installed as a sand-boxed environment to build stableDracor instances. 
To get into the container use `docker exec -it dracor-builder /bin/sh`. 
Jupyter lab is available at http://localhost:8888

## See also
For a use-case of a Stable DraCor System in research see our paper 
[Detecting Small Worlds in a Corpus of Thousands of Theater Plays](https://github.com/dracor-org/small-world-paper/tree/publication-version).
For information on the internal workings of the DraCor system see the report [On Programmable Corpora](https://doi.org/10.5281/zenodo.7664964) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7664964.svg)](https://doi.org/10.5281/zenodo.7664964).

## Acknowledgment
The development of this package was supported by the project [Computational Literary Studies Infrastructure](https://clsinfra.io) (CLS INFRA). 
CLS INFRA has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 101004984.