## Full stack of DraCor services
Run a complete local stack of DraCor services (API, frontend, metrics service, triple store)
``docker compose -f compose.fullstack.empty.yml up`
User `admin`, Password is empty

## Jupyter lab with kernel
with `pyenv` and `pyenv-virtualenv` installed:
create a virtual environment `pyenv virtualenv 3.11.3 stable-dracor`
install ipykernel (and jupyter lab); install the kernel spec
`python -m ipykernel install --user --name stable-dracor --display-name "Python (stable-dracor)"`
