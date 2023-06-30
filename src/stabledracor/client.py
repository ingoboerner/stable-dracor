"""Client to manage a local Docker-based instance of DraCor"""

import requests, json
from requests.auth import HTTPBasicAuth
from requests import ConnectionError
import logging
import uuid
import os
from xml.etree.ElementTree import ParseError
from xml.etree import ElementTree as ET
import base64
import subprocess
import yaml
from datetime import datetime
import time
import hashlib


def construct_request_url(
    api_base_url: str = "https://dracor.org/api/",
    corpusname: str = None,
    playname: str = None,
    method: str = None):
    """Construct the request url

    Args:
        api_base_url (str, optional): Base URL of the DraCor API.
        corpusname (str, optional): Identifier of corpus 'corpusname'.
        playname (str, optional): Identifier of play 'playname'.
        method (str, optional): API method, e.g. "tei", "cast", ...
    """

    if api_base_url.endswith("/"):
        pass
    else:
        api_base_url = api_base_url + "/"

    if corpusname and playname:
        if method:
            request_url = f"{api_base_url}corpora/{corpusname}/play/{playname}/{method}"
        else:
            request_url = f"{api_base_url}corpora/{corpusname}/play/{playname}"
    elif corpusname and not playname:
        if method:
            request_url = f"{api_base_url}corpora/{corpusname}/{method}"
        else:
            request_url = f"{api_base_url}corpora/{corpusname}"
    elif method and not corpusname and not playname:
        request_url = f"{api_base_url}{method}"
    else:
        request_url = f"{api_base_url}info"

    return request_url


def api_get(
        api_base_url: str = "https://dracor.org/api/",
        corpusname: str = None,
        playname: str = None,
        method: str = None,
        parse_json: bool = True):
    """Send GET request to a DraCor API

    Args:
        api_base_url (str, optional): Base URL of the DraCor API.
        corpusname (str, optional): Identifier of corpus 'corpusname'.
        playname (str, optional): Identifier of play 'playname'.
        method (str, optional): API method, e.g. "tei", "cast", ...
        parse_json (bool, optiona): Parse the result as JSON. Defaults to True.

    """
    request_url = construct_request_url(api_base_url=api_base_url,
                                        corpusname=corpusname,
                                        playname=playname,
                                        method=method)

    logging.debug(f"Will send GET request to: {request_url}")

    r = requests.get(request_url)

    assert r.status_code == 200, "Request was not successful. Server returned status code: " + str(r.status_code)

    if method == "tei":
        logging.debug("Requested TEI-XML, encoded in UTF-8.")
        return r.text.encode("utf-8")
    elif parse_json is True:
        json_data = json.loads(r.text)
        logging.debug("Parsed response to JSON.")
        return json_data
    else:
        logging.debug("Return data as is.")
        return r.text


def api_post(
        data,
        api_base_url: str = "https://dracor.org/api/",
        corpusname: str = None,
        playname: str = None,
        method: str = None,
        username: str = "admin",
        password: str = "",
        headers: dict = None,
        payload_format: str = "json"):
    """Send POST request to a DraCor API

    Args:
        data: Data to include in the body of the POST request.
        api_base_url (str, optional): Base URL of the DraCor API.
        corpusname (str, optional): Identifier of corpus 'corpusname'.
        playname (str, optional): Identifier of play 'playname'.
        method (str, optional): API method, e.g. "tei", "cast", ...
        username (str, optional): Username of a user with write access. Defaults to "admin"
        password (str, optional): Password. Defaults to empty string ""
        headers (str, optional): Headers to include in the POST request
        payload_format (str, optional): Format of the payload. Defaults to "json".
    """
    request_url = construct_request_url(api_base_url=api_base_url,
                                        corpusname=corpusname,
                                        playname=playname,
                                        method=method)

    logging.debug(f"Will send POST request to: {request_url}")

    if username is not None and password is not None:
        logging.debug("Username and Password are set.")
        credentials = HTTPBasicAuth(username, password)
    else:
        logging.debug("Username and Password are NOT set.")
        credentials = None

    if data and headers and credentials:
        logging.debug("Send POST request with data, headers and credentials.")
        if payload_format == "json":
            r = requests.post(request_url, json=data, headers=headers, auth=credentials)
        else:
            r = requests.post(request_url, data=data, headers=headers, auth=credentials)
        logging.debug(f"Executed POST request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    elif data and credentials and not headers:
        logging.debug("Send POST request with data and credentials, not headers.")
        if payload_format == "json":
            r = requests.post(request_url, json=data, auth=credentials)
        else:
            r = requests.post(request_url, data=data, auth=credentials)
        logging.debug(f"Executed POST request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    elif data and headers and not credentials:
        logging.debug("Send POST request with data and headers, no credentials.")
        if payload_format == "json":
            r = requests.post(request_url, json=data, headers=headers)
        else:
            r = requests.post(request_url, data=data, headers=headers)
        logging.debug(f"Executed POST request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    else:
        logging.debug("Send POST request without anything, only request url.")
        r = requests.post(request_url)
        return r.status_code


def api_put(data,
        api_base_url: str = "https://dracor.org/api/",
        corpusname: str = None,
        playname: str = None,
        method: str = None,
        username: str = "admin",
        password: str = "",
        headers: dict = None):
    """Send PUT request to a DraCor API

        Args:
            data: Data to include in the body of the POST request.
            api_base_url (str, optional): Base URL of the DraCor API.
            corpusname (str, optional): Identifier of corpus 'corpusname'.
            playname (str, optional): Identifier of play 'playname'.
            method (str, optional): API method, e.g. "tei", "cast", ...
            username (str, optional): Username of a user with write access. Defaults to "admin"
            password (str, optional): Password. Defaults to empty string
            headers (dict, optional): HTTP headers to send with the request""
        """
    request_url = construct_request_url(api_base_url=api_base_url,
                                        corpusname=corpusname,
                                        playname=playname,
                                        method=method)

    logging.debug(f"Will send PUT request to: {request_url}")

    if username is not None and password is not None:
        logging.debug("Credentials are provided.")
        credentials = HTTPBasicAuth(username, password)
    else:
        logging.debug("Credentials are not provided.")
        credentials = None

    if data and headers and credentials:
        r = requests.put(request_url, data=data, headers=headers, auth=credentials)
        logging.debug(f"Executed PUT request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    elif data and credentials and not headers:
        r = requests.put(request_url, data=data, auth=credentials)
        logging.debug(f"Executed PUT request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    elif data and headers and not credentials:
        r = requests.put(request_url, data=data, headers=headers)
        logging.debug(f"Executed PUT request. Server returned status code: {str(r.status_code)}")
        return r.status_code

    else:
        r = requests.put(request_url)
        logging.debug(f"Executed PUT request. Server returned status code: {str(r.status_code)}")
        return r.status_code


def api_delete(
        api_base_url: str = "https://dracor.org/api/",
        corpusname: str = None,
        playname: str = None,
        method: str = None,
        username: str = "admin",
        password: str = "",
        headers: dict = None):
    """Set DELETE request to a DraCor API

    Args:
        api_base_url (str, optional): Base URL of the DraCor API.
        corpusname (str, optional): Identifier of corpus 'corpusname'.
        playname (str, optional): Identifier of play 'playname'.
        method (str, optional): API method, e.g. "tei", "cast", ...
        username (str, optional): Username of a user with write access. Defaults to "admin"
        password (str, optional): Password. Defaults to empty string
        headers (dict, optional): HTTP headers to send with the request""
    """
    request_url = construct_request_url(api_base_url=api_base_url,
                                        corpusname=corpusname,
                                        playname=playname,
                                        method=method)

    logging.debug(f"Will send DELETE request to: {request_url}")

    if username is not None and password is not None:
        logging.debug("Credentials are provided.")
        credentials = HTTPBasicAuth(username, password)
    else:
        logging.debug("Credentials are not provided.")
        credentials = None

    if credentials and headers:
        r = requests.delete(request_url, headers=headers, auth=credentials)
        logging.debug(f"Executed DELETE request including headers and credentials. "
                      f"Server returned status code: {str(r.status_code)}")
        return r.status_code
    elif credentials and not headers:
        r = requests.delete(request_url, auth=credentials)
        logging.debug(f"Executed DELETE request including credentials, but no headers. "
                      f"Server returned status code: {str(r.status_code)}")
        return r.status_code
    else:
        r = requests.delete(request_url)
        logging.debug(f"Executed DELETE request (no headers, no credentials). "
                      f"Server returned status code: {str(r.status_code)}")
        return r.status_code


"""
Some ideas that have not been implemented yet:

- In parallel to corpora in the DB, the class should keep track of the status, e.g. information, if a play has been 
removed, added, ... so that it is always possible to retrieve a manifest file of a given corpus.
- store a corpus that has been compiled to a git repo, e.g. when adding plays from local, ... this is useful, when 
there are changes necessary that can't be included in DraCor but want to be persisted.
- change metadata of a corpus (there is no API function for this)
- lookup function DraCor - ID to corpusname+playname and vice versa
"""


class StableDraCor:
    """Stable Local DraCor instance
    """

    # URLs of external DraCor APIs
    __dracor_api_urls = dict(
        production="https://dracor.org/api/",
        staging="https://staging.dracor.org/api/",
    )

    def __init__(self,
                 api_base_url: str = None,
                 username: str = None,
                 password: str = None,
                 name: str = None,
                 description: str = None,
                 github_access_token: str = None,
                 manifest: dict = None):
        """

        Args:
             api_base_url (str, optional): URL of the local DraCor API. Default is set to http://localhost:8088/api/
             username (str, optional): Username of the local instance. Default is set to "admin"
             password (str, optional): Password of the admin user of the local instance. Default is set to ""
             name (str, optional): Name of the local instance
             description (str, optional): Description of the local instance
             github_access_token (str, optional): Github Personal Access token used to indentify
                when sending API requests to the GitHub API. Allows for higher rate limit then anonymous requests.
            manifest (dict, optional): Manifest describing a system with pre-loaded corpora
        """

        # Set a uuid
        self.__id = uuid.uuid4()
        logging.debug(f"Generated ID: {self.__id}.")

        # Create a system from a provided manifest
        if manifest is not None:
            logging.warning("Creating a system from a manifest is not implemented yet.")

        if name is not None:
            logging.debug(f"Set name to: {name}")
            self.__name = name
        else:
            self.__name = None

        if description is not None:
            logging.debug(f"Set description to: {name}")
            self.__description = description
        else:
            self.__description = None

        if api_base_url is not None:
            logging.debug(f"Update api_base_url with: {api_base_url}")
            self.__api_base_url = api_base_url
        else:
            self.__api_base_url = "http://localhost:8088/api/"

        if username is not None:
            logging.debug(f"Update username with: {api_base_url}")
            self.__username = username
        else:
            logging.debug("Using default username 'admin'.")
            self.__username = "admin"

        if password is not None:
            logging.debug(f"Update password with: {api_base_url}")
            self.__password = password
        else:
            logging.debug("Using default password: ''.")
            self.__password = ""

        logging.info(f"Initialized new StableDraCor instance: '{self.__name}' (ID: {self.__id}).")

        if self.__test_api_connection() is True:
            logging.info(f"Local DraCor API is available at {self.__api_base_url}.")
        else:
            logging.warning(f"Local DraCor API is not available at {self.__api_base_url}.")

        if github_access_token is not None:
            self.__github_access_token = github_access_token
        else:
            self.__github_access_token = None
            logging.warning("Personal GitHub Access Token is not supplied. Requests to the GitHub API might be affected"
                            " by rate limiting.")

        # Check for the Operation System. Will output a Warning if working on Windows ;)
        self.__check_operation_system()

        # Check if Docker is installed. Will issue a warning if not
        self.__check_docker_installed()

        # Docker services
        # Initially assume, that there are no services running, but try to locate them in the next step
        self.__services = dict(
            api=None,
            frontend=None,
            metrics=None,
            triplestore=None
        )

        # Try to detect running docker services
        self.__detect_docker_services()

        # List of images to push to dockerhub when calling the method
        self.__images_to_be_pushed = []

        # docker-compose file
        self.__docker_compose_file = None

        # Metadata on loaded corpora
        self.__corpora = {}

    def __prepare_system_metadata(self) -> dict:
        """Helper funtion to prepare metadata on running system"""

        metadata = dict(
            id=str(self.__id)
        )

        if self.__name:
            metadata["name"] = self.__name

        if self.__description:
            metadata["description"] = self.__description

        now = datetime.now()
        metadata["timestamp"] = now.isoformat()

        return metadata

    def get_manifest(self):
        """Get manifest of the running system"""

        manifest = dict(
            version="v1",
            system=self.__prepare_system_metadata(),
            services=self.__services,
            corpora=self.__corpora
            )

        # Add additional information to the api service
        api_info = self.get_api_info()
        if "version" in api_info:
            if "api" in self.__services:
                manifest["services"]["api"]["version"] = api_info["version"]

        if "existdb" in api_info:
            if "api" in self.__services:
                manifest["services"]["api"]["existdb"] = api_info["existdb"]

        # add number of plays to corpora
        try:
            corpora_metrics = self.__get_corpora_metrics_for_manifest()
        except:
            logging.debug("Retrieving metrics of corpora failed.")
            corpora_metrics = dict()

        #logging.debug(corpora_metrics)

        for corpus_metrics_key in corpora_metrics.keys():
            if corpus_metrics_key in manifest["corpora"]:
                corpus_metrics = corpora_metrics[corpus_metrics_key]
                if "num_of_plays" in corpus_metrics:
                    manifest["corpora"][corpus_metrics_key]["num_of_plays"] = int(corpus_metrics["num_of_plays"])

        return manifest

    def __api_get(self, **kwargs):
        """Send GET request to running local instance. Uses the function api_get, but overrides api_base_url
        with the URL of the local instance"""
        try:
            result = api_get(api_base_url=self.__api_base_url, **kwargs)
            return result
        except AssertionError as err:
            # This is probably because the eXist-DB is not ready; it returns status code 502
            logging.debug(f"Caught exception: {str(err)}.")
            raise ConnectionError("Can not establish connection.")

    def __wait_for_api_connection(self, max_retries: int = 10) -> bool:
        """Helper function to periodically check connection to DraCor API"""
        connection = False
        attempts = max_retries

        while connection is False:
            try:
                self.get_api_info()
                connection = True
            except ConnectionError:
                attempts = attempts - 1
                logging.debug(f"Connection not successful. Will retry in 5 seconds. {str(attempts)} attempts left.")
                time.sleep(5)
            if attempts <= 0:
                logging.debug(f"Can not connect to API after {max_retries}. Giving up.")
                return False

        return True

    def __api_post(self, data, **kwargs):
        """Send POST request to running local instance. Uses the function api_post, but overrides api_base_url
        with the URL of the local instance

        Args:
            data: Payload to include in body

        """

        logging.debug(kwargs)
        return api_post(data, api_base_url=self.__api_base_url, **kwargs)

    def __api_put(self, data, **kwargs):
        """Send PUT request to running local instance. Uses the function api_put, but overrides api_base_url
        with the URL of the local instance

        Args:
            data: Payload to include in body
        """
        logging.debug(kwargs)
        return api_put(data, api_base_url=self.__api_base_url, **kwargs)

    def __api_delete(self, **kwargs):
        """Send DELETE request to running local instance. Uses the function api_delete, but overrides api_base_url
        with the URL of the local instance
        """
        logging.debug(kwargs)
        return api_delete(api_base_url=self.__api_base_url, **kwargs)

    def __test_api_connection(self):
        """Test if local DraCor API is available."""
        try:
            self.__api_get()
            return True
        except ConnectionError:
            logging.debug("No API connection.")
            return False

    def __github_api_get(self,
                         api_call: str = None,
                         url: str = None,
                         headers: dict = None,
                         parse_json: bool = True,
                         **kwargs):
        """Send GET requests to the GitHub API.

        Args:
            api_call (str, optional): endpoint and parameters that should be sent to the GitHub API.
            url (str, optional): Full URL to GET data from GitHub API. If provided, api_call will be ignored.
            headers (dict, optional): Headers to send with the GET request. If provided on class instance level,
                will include the "Authorization" field with value of the personal access token and thus send authorized
                requests.
            parse_json (bool, optional): Parse the response as JSON. Defaults to True.

        """
        # Base-URL of the GitHub API
        github_api_base_url = "https://api.github.com/"

        if self.__github_access_token is not None:
            if headers is not None:
                headers["Authorization"] = f"Bearer {self.__github_access_token}"
            else:
                headers = dict(
                    Authorization=f"Bearer {self.__github_access_token}"
                )

        if api_call is not None and url is None:
            request_url = f"{github_api_base_url}{api_call}"
            logging.debug(f"Send GET request to GitHub: {request_url}")
        elif url is not None:
            request_url = url
            logging.debug(f"Provided full URL to send GET request to GitHub: {request_url}.")
        else:
            request_url = github_api_base_url
            logging.debug(f"No specialized API call (api_call) provided. Will send GET request to GitHub API "
                          f" base url.")

        if headers is not None:
            r = requests.get(url=request_url, headers=headers)
        else:
            r = requests.get(url=request_url)

        # logging.debug(r.headers)
        if "X-RateLimit-Remaining" in r.headers:
            if 1 < int(r.headers["X-RateLimit-Remaining"]) < 5:
                logging.warning(f"Approaching maximum API calls (rate limit). Remaining: "
                                f" {r.headers['X-RateLimit-Remaining']}")
            elif int(r.headers["X-RateLimit-Remaining"] == 1):
                logging.warning(f"Reached rate limit of {r.headers['X-RateLimit-Limit']}.")
                if self.__github_access_token is None:
                    logging.warning("Requests to GitHub API are probably unauthorized. Provide a personal "
                                    "access token to get a higher rate limit. "
                                    "See: https://docs.github.com/en/authentication/"
                                    "keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
                                    "#creating-a-personal-access-token-classic")

        if r.status_code == 200:
            logging.debug(f"GET request to GitHub API was successful.")
            if parse_json is True:
                data = json.loads(r.text)
                return data
            else:
                return r.text
        # TODO implement the other status codes
        else:
            logging.debug(f"GET request was not successful. Server returned status code: {str(r.status_code)}.")
            logging.debug(r.text)

    def __check_docker_installed(self):
        """Helper Function to test if Docker is installed and can execute commands"""
        run_check = subprocess.run(["docker", "--version"], capture_output=True)
        docker_version_string = run_check.stdout.decode("utf-8")

        if "Docker version" in docker_version_string:
            logging.info(f"Docker is available.")
            return True
        else:
            logging.warning("Docker is not available and/or can not run subprocesses."
                            "Install Docker Desktop: https://www.docker.com/products/docker-desktop/")
            return False

    def __check_operation_system(self):
        """Helper Function to check if running on Windows."""
        operation_system = os.name
        logging.debug(f"Detected Operation System Type: '{operation_system}'")

        if operation_system == 'nt':
            logging.warning("The client has not been tested on Windows. There might be some limitations regarding "
                            " the management of Docker images/containers. Please report any bugs.")

        return operation_system

    def list_docker_images(self):
        """List Docker images available"""
        # docker images repo1 --format "{{json . }}"
        operation = subprocess.run(["docker", "images", "--format", '{{json . }}'], capture_output=True)
        items = operation.stdout.decode("utf-8").split("\n")
        images = []
        for item in items:
            if item != "":
                image = json.loads(item)
                images.append(image)
        return images

    def get_labels_from_docker_image(self, id: str) -> dict:
        """Extract labels from a docker image identified by its image ID

        Args:
            id (str): ID of the image

        Returns:
            dict: Docker image labels
        """

        operation = subprocess.run(["docker",
                                    "inspect",
                                    f"{id}",
                                    "--format",
                                    '{{ json .Config.Labels }}'
                                    ], capture_output=True)

        return json.loads(operation.stdout.decode())

    def __docker_labels_to_manifest(self, labels: dict):
        """Helper Function to convert labels (org.dracor.stable-dracor) of a docker image to a manifest
        """

        label_list = list(labels.keys())

        manifest = dict(
            system={},
            services={},
            corpora={}
        )

        if "org.dracor.stable-dracor.version" in labels:
            manifest["version"] = labels["org.dracor.stable-dracor.version"]

        # System:
        # all labels starting with: "org.dracor.stable-dracor.system."
        system_labels = list(filter(lambda label: label.startswith("org.dracor.stable-dracor.system."), label_list))
        for system_label in system_labels:
            system_key = system_label.replace("org.dracor.stable-dracor.system.", "")
            manifest["system"][system_key] = labels[system_label]

        # Services:
        if "org.dracor.stable-dracor.services" in label_list:
            service_keys = labels["org.dracor.stable-dracor.services"].split(",")
            for service_key in service_keys:
                manifest["services"][service_key] = {}
                this_service_labels = list(filter(lambda label:
                                                  label.startswith(f"org.dracor.stable-dracor.services.{service_key}."),
                                                  label_list))
                for this_service_label_key in this_service_labels:
                    this_service_data_key = this_service_label_key.replace(
                        f"org.dracor.stable-dracor.services.{service_key}.", "")
                    manifest["services"][service_key][this_service_data_key] = labels[this_service_label_key]

        # Corpora:
        if "org.dracor.stable-dracor.corpora" in label_list:
            corpus_keys = labels["org.dracor.stable-dracor.corpora"].split(",")
            for corpus_key in corpus_keys:
                corpus = {}
                if f"org.dracor.stable-dracor.corpora.{corpus_key}.corpusname" in labels:
                    corpus["corpusname"] = labels[f"org.dracor.stable-dracor.corpora.{corpus_key}.corpusname"]
                if f"org.dracor.stable-dracor.corpora.{corpus_key}.num-of-plays" in labels:
                    corpus["num_of_plays"] = labels[f"org.dracor.stable-dracor.corpora.{corpus_key}.num-of-plays"]

                # get the sources of a corpus
                if f"org.dracor.stable-dracor.corpora.{corpus_key}.sources" in labels:
                    corpus["sources"] = {}
                    source_keys = labels[f"org.dracor.stable-dracor.corpora.{corpus_key}.sources"].split(",")
                    for source_key in source_keys:
                        source = dict()
                        source_labels = list(
                            filter(lambda label: label.startswith(f"org.dracor.stable-dracor.corpora.{corpus_key}."
                                                                  f"sources.{source_key}."), label_list))
                        for source_label in source_labels:
                            source_data_key = source_label.replace(f"org.dracor.stable-dracor.corpora.{corpus_key}."
                                                                   f"sources.{source_key}.", "")
                            if "." in source_data_key:
                                # this creates the part "exclude" or "include"
                                include_exclude_key = source_data_key.split(".")[0]
                                include_exclude_field_key = source_data_key.split(".")[1]
                                if include_exclude_key not in source:
                                    source[include_exclude_key] = {}
                                include_exclude_field_label = f"org.dracor.stable-dracor.corpora.{corpus_key}."\
                                                              f"sources.{source_key}.{include_exclude_key}." \
                                                              f"{include_exclude_field_key}"
                                if include_exclude_field_key == "ids":
                                    include_exclude_field_value = labels[include_exclude_field_label].split(",")
                                else:
                                    include_exclude_field_value = labels[include_exclude_field_label]

                                source[include_exclude_key][include_exclude_field_key] = include_exclude_field_value

                            else:
                                source[source_data_key] = labels[source_label]

                        corpus["sources"][source_key] = source

                manifest["corpora"][corpus_key] = corpus

        return manifest

    def create_manifest(self, image: str = None) -> dict:
        """

        Args:
            image: ID of a StableDraCor docker image

        Returns:
            dict: Manifest describing DraCor system

        """
        if image is not None:
            logging.debug(f"Generating manifest from docker labels of image {image}.")
            image_labels = self.get_labels_from_docker_image(id=image)
            return self.__docker_labels_to_manifest(image_labels)

    def list_docker_containers(self,
                               only_running: bool = False) -> list:
        """

        Args:
            only_running (bool): Filter on running containers. Defaults to False

        Returns:
            list: Containers
        """
        if only_running is True:
            operation = subprocess.run(["docker", "ps", "--format", '{{json . }}'], capture_output=True)
        else:
            operation = subprocess.run(["docker", "ps", "-a", "--format", '{{json . }}'], capture_output=True)

        items = operation.stdout.decode("utf-8").split("\n")

        containers = []
        for item in items:
            if item != "":
                container = json.loads(item)
                containers.append(container)

        return containers

    def __detect_single_docker_service(self,
                                       name: str,
                                       expected_image: str,
                                       containers: list = None
                                       ):
        """Detect a single running Docker service based on the image used. We assume, that
        the containers are build with the standard images, e.g. dracor/dracor-api, ... and that we can filter
        for that.

        Args:
            name (str): Common name of the service, e.g. "api", "frontend", "tiplestore", "metrics"
            expected_image (str): Filter the containers by image. We look for the standard images, e.g.
                "dracor/dracor-api"
            containers (list, optional): A list of containers that will be filtered based on the expected_image
        """

        if containers is None:
            # if not set, get the running containers
            containers = self.list_docker_containers(only_running=True)

        container = list(filter(lambda item: f"{expected_image}" in item["Image"], containers))

        if len(container) == 0:
            logging.warning(f"Could not detect a running Docker container derived from a {expected_image} image.")
        elif len(container) == 1:
            container_id = container[0]["ID"]
            image = container[0]["Image"]
            logging.info(f"Found {expected_image} container with ID {container_id}. Image is: {image}")

            if self.__services[name] is None:
                self.set_service(name=name, container=container_id, image=image)
            else:
                if "container" in self.__services[name]:
                    if self.__services[name]["container"] == container_id:
                        logging.debug(f"Container {name} already registered.")
                    else:
                        logging.warning(f"A different Docker container (ID: {self.__services[name]['container']}) is"
                                        f" already registered as service {name}.")
                        logging.debug(f"Already registered container: {self.__services[name]['container']}.")
                        logging.debug(f"Container that should be registered now: {container_id}.")

        else:
            logging.warning(f"Found {len(container)} running Docker containers derived from a '{expected_image}' "
                            f"image. Can not automatically detect if it is the database that shall be used. "
                            f"Set the container manually!")

    def __detect_docker_services(self):
        """Helper function to detect running services.

        can do this based on the image or the port?
         e.g. 'Ports': '0.0.0.0:8080->8080/tcp', (Port would probably be the better option for API/frontend)
        Ideally only one container would be running. This would be the container to work with."""

        running_containers = self.list_docker_containers(only_running=True)
        if len(running_containers) == 0:
            logging.debug("No running Docker containers found.")
        else:
            logging.debug(f"Detected {len(running_containers)} running Docker containers.")
            # logging.debug(running_containers)

        expected_service_images = dict(
            api="dracor/dracor-api",
            frontend="dracor/dracor-frontend",
            metrics="dracor/dracor-metrics",
            triplestore="dracor/dracor-fuseki"
        )

        for service_name in expected_service_images.keys():
            self.__detect_single_docker_service(name=service_name,
                                                expected_image=expected_service_images[service_name],
                                                containers=running_containers)

        # API/eXist could also be derived from dracor/stable-dracor:{tag} this should be also checked
        if self.__services["api"] is None:
            self.__detect_single_docker_service(name="api",
                                                expected_image="dracor/stable-dracor",
                                                containers=running_containers)

    def __run_services_with_docker_compose(self,
                                           compose_file: str = None,
                                           url: str = None,
                                           fetch_default_compose: bool = False):
        """Run services with a docker compose file. Can use either a local compose file or use one that is
        downloaded from a URL.

        Args:
            compose_file (str, optional): Path to a compose file.
            url (str, optional): URL to a compose file.
            fetch_default_compose (bool, optional): Flag to trigger fetching default docker compose file from GitHub.
                Defaults to False
        """
        if self.__name:
            stack_name = self.__name
        else:
            stack_name = "stable-dracor"

        if compose_file is None:

            if url is not None:
                r = requests.get(url=url)
                if r.status_code == 200:
                    logging.debug(f"Downloaded file from {url}. Will try stating services based on this file.")
                    compose_file_raw = r.text
                else:
                    logging.warning(f"Can not download file from {url}. Check provided URL or internet connection.")

            elif fetch_default_compose is True:
                # This happens if nothing is specified!
                compose_file_raw = self.__get_default_docker_compose()

            else:
                logging.warning(f"No compose file specified. Can not run services.")

            compose_file_bytes = bytes(compose_file_raw, "utf-8")

            operation = subprocess.run(["docker",
                                        "compose",
                                        "-p",
                                        f"{stack_name}",
                                        "-f",
                                        "-",
                                        "up",
                                        "-d"], input=compose_file_bytes)

            logging.info(f"Started with downloaded docker compose file.")

        elif compose_file is not None:

            operation = subprocess.run(["docker",
                                        "compose",
                                        "-p",
                                        f"{stack_name}",
                                        "-f",
                                        compose_file,
                                        "up",
                                        "-d"])
            logging.debug(f"Started with docker compose file {compose_file}")
            self.__docker_compose_file = compose_file

            return True

        else:
            logging.warning("Can not start containers. Compose file not specified.")

    def __get_default_docker_compose(self):
        """Helper function to get a docker compose file to run an empty stack with. This is a fallback
        to make running a local instance easy.
        TODO: rework this method
        """
        # The default URL of the compose file is hardcoded. It might be necessary to use different configurations
        # depending on the operation system.
        url = "https://raw.githubusercontent.com/dracor-org/stabledracor/master/configurations/compose.fullstack.empty.yml"

        r = requests.get(url=url)
        if r.status_code == 200:
            compose_file = r.text
            logging.info(f"Fetched default compose file (configuration) from {url}.")
            return compose_file
        else:
            logging.warning(f"Could not retrieve compose file. Server returned status code {str(r.status_code)}.")

    def run(self,
            compose_file: str = None,
            url: str = None) -> bool:
        """Run a stack of DraCor Services.
            If no compose file is provided, a compose file will be fetched from the project repository on Github.

        Args:
            compose_file (str, optional): Path to a docker compose file that defines the services
            url (str, optional): URL of a compose file

        Returns:
            bool: True if successful.
        """
        if compose_file is None and url is None:
            self.__run_services_with_docker_compose(fetch_default_compose=True)
        elif url is not None:
            self.__run_services_with_docker_compose(url=url)
        elif compose_file is not None:
            self.__run_services_with_docker_compose(compose_file=compose_file)

        # Try to detect running docker services
        self.__detect_docker_services()

        # this will try to get the API info, try 10 times, wait 5 seconds between the attempts; if
        # a connection can be established it will return true
        logging.info("Trying to connect to the local DraCor API. This can take some time ...")
        api_connection_status = self.__wait_for_api_connection()

        if api_connection_status is False:
            logging.warning(f"Can not establish API connection. Tested with '{self.__api_base_url}/info'.")
            return False
        else:
            logging.info(f"DraCor API can be reached at '{self.__api_base_url}'.")
            return True

    def __stop_docker_container_by_id(self, container_id:str):
        """Helper Function to stop a single Docker container identified by its ID"""
        stop_operation = subprocess.run(["docker", "stop", f"{container_id}"])

    def __stop_docker_stack(self):
        """Helper function to stop the whole docker stack
        docker compose -f {compose_file} stop does not work – maybe because of the containers
        running in detached mode, therefore we stop all containers in self.__services..
        TODO: this should maybe return a status
        """
        for key in self.__services.keys():
            container = self.__services[key]["container"]
            self.__stop_docker_container_by_id(container)
            logging.info(f"Stopped container '{container}'.")

    def stop(self,
             container: str = None,
             service: str = None
             ):
        """Stop the whole stack (if no container ID supplied; or a single container)"""
        if container is not None and service is None:
            self.__stop_docker_container_by_id(container)
            logging.debug(f"Stopping container {container}.")
        elif service is not None and container is None:
            container = self.__services[service]["container"]
            self.__stop_docker_container_by_id(container)
            logging.info(f"Stopping service '{service}' running as container {container}.")
        else:
            if self.__docker_compose_file is not None:
                logging.debug("Stopping all services.")
                self.__stop_docker_stack()
            else:
                logging.warning("Can not stop stack. No compose file is set.")

    def set_service(self,
                    name: str,
                    container: str,
                    image: str = None) -> dict:
        """Register a service (docker container) with the client

        Args:
            name (str): Name of the service (one of "api","frontend","metrics","triplestore")
            container (str): ID of the docker container running the service
            image (str, optional): Name/Tag of the image the container is based on

        Returns:
            dict: data on the service
        """
        if name not in ["api", "frontend", "metrics", "triplestore"]:
            logging.warning(f"Registering a non-canonical service: {name}")

        if self.__services[name] is None:
            self.__services[name] = dict(container=container)
        else:
            self.__services[name]["container"] = container

        if image is not None:
            self.__services[name]["image"] = image

        return self.__services[name]

    def __get_corpora_metrics_for_manifest(self) -> dict:
        """Helper Function to extract some data from the corpus metrics to be included in the manifest
        Currently, only the number of plays "num_of_plays" is included
        """
        corpora = self.__api_get(method="corpora?include=metrics")
        logging.debug("Retrieved corpus metrics")
        # logging.debug(corpora)

        metrics = dict()

        for item in corpora:
            corpus = dict()
            if "metrics" in item:
                if "plays" in item["metrics"]:
                    corpus["num_of_plays"] = item["metrics"]["plays"]
                # only if it has metrics
                metrics[item["name"]] = corpus

        return metrics

    def __create_docker_image_labels(self,
                                     service: str = "api",
                                     this_image: str = None,
                                     base_image: str = None):
        """
        Helper Function to create Docker Labels to append when committing an image
        Creates a string that can be used in the docker commit command with the option -c or --change, e.g.
        LABEL multi.label1="value1" multi.label2="value2" other="value3"

        Args:
            service (str, optional): Name of the service for which the image the labels are created for.
                Defaults to "api"
            this_image (str, optional): "New" image that the labels are created for
            base_image (str, optional): Image that the new image is based on (normally a canonical dracor-api image)
        """

        manifest = self.get_manifest()

        label_data = {}

        label_data["org.dracor.stable-dracor.version"] = manifest["version"]

        # Data of the System org.dracor.stable-dracor.system.*
        label_data["org.dracor.stable-dracor.system.id"] = manifest["system"]["id"]

        if "name" in manifest["system"]:
            label_data["org.dracor.stable-dracor.system.name"] = manifest["system"]["name"]

        if "description" in manifest["system"]:
            label_data["org.dracor.stable-dracor.system.description"] = manifest["system"]["description"]

        if "timestamp" in manifest["system"]:
            label_data["org.dracor.stable-dracor.system.timestamp"] = manifest["system"]["timestamp"]

        corpusnames = list(manifest["corpora"].keys())
        if len(corpusnames) > 0:
            label_data["org.dracor.stable-dracor.corpora"] = ",".join(corpusnames)

        for corpus_key in corpusnames:
            if "corpusname" in manifest["corpora"][corpus_key]:
                label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.corpusname"
                label_data[label_key] = manifest["corpora"][corpus_key]["corpusname"]
            if "timestamp" in manifest["corpora"][corpus_key]:
                label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.timestamp"
                label_data[label_key] = manifest["corpora"][corpus_key]["timestamp"]
            if "num_of_plays" in manifest["corpora"][corpus_key]:
                label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.num-of-plays"
                label_data[label_key] = str(manifest["corpora"][corpus_key]["num_of_plays"])

            # Sources of a corpus: org.dracor.stable-dracor.corpora.{corpusname}.sources.*
            if "sources" in manifest["corpora"][corpus_key]:
                label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources"
                label_data[label_key] = ",".join(list(manifest["corpora"][corpus_key]["sources"].keys()))

                # Data of a source of a corpus: org.dracor.stable-dracor.corpora.{corpusname}.sources.{sourcename}.*
                for source_key in manifest["corpora"][corpus_key]["sources"].keys():
                    source = manifest["corpora"][corpus_key]["sources"][source_key]
                    if "corpusname" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}.corpusname"
                        label_data[label_key] = source["corpusname"]
                    if "type" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}.type"
                        label_data[label_key] = source["type"]
                    if "url" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}.url"
                        label_data[label_key] = source["url"]
                    if "timestamp" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}.timestamp"
                        label_data[label_key] = source["timestamp"]
                    if "commit" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}.commit"
                        label_data[label_key] = source["commit"]
                    if "exclude" in source:
                        if "type" in source["exclude"]:
                            label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}." \
                                        f"exclude.type"
                            label_data[label_key] = source["exclude"]["type"]
                        if "ids" in source["exclude"]:
                            label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}." \
                                        f"exclude.ids"
                            label_data[label_key] = ",".join(source["exclude"]["ids"])
                    if "include" in source:
                        if "type" in source["include"]:
                            label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}." \
                                        f"include.type"
                            label_data[label_key] = source["include"]["type"]
                        if "ids" in source["include"]:
                            label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}." \
                                        f"include.ids"
                            label_data[label_key] = ",".join(source["include"]["ids"])
                    if "num_of_plays" in source:
                        label_key = f"org.dracor.stable-dracor.corpora.{corpus_key}.sources.{source_key}." \
                                    f"num-of-plays"
                        label_data[label_key] = source["num_of_plays"]

        # Data on the services: org.dracor.stable-dracor.services.*
        service_names = []
        for service_key in manifest["services"].keys():
            if service_key == service:
                service_names.append(service)
                if base_image is not None:
                    label_key = f"org.dracor.stable-dracor.services.{service_key}.base-image"
                    label_data[label_key] = base_image
                if this_image is not None:
                    label_key = f"org.dracor.stable-dracor.services.{service_key}.image"
                    label_data[label_key] = this_image

            else:
                if manifest["services"][service_key] is not None:
                    service_names.append(service_key)
                    if "image" in manifest["services"][service_key]:
                        label_key = f"org.dracor.stable-dracor.services.{service_key}.image"
                        label_data[label_key] = manifest["services"][service_key]["image"]

        # Add additional info if committing API container
        if service == "api":
            if "api" in manifest["services"]:
                if "existdb" in manifest["services"]["api"]:
                    label_key = f"org.dracor.stable-dracor.services.api.existdb"
                    label_data[label_key] = manifest["services"]["api"]["existdb"]
                if "version" in manifest["services"]["api"]:
                    label_key = f"org.dracor.stable-dracor.services.api.version"
                    label_data[label_key] = manifest["services"]["api"]["version"]

        if len(service_names) > 0:
            # somehow json dumps does not work: tested json.dumps(service_names, separators=(',', ':'))
            label_data["org.dracor.stable-dracor.services"] = ",".join(service_names)

        labels = []

        for key in label_data.keys():
            label_string = f'{key}="{label_data[key]}"'
            labels.append(label_string)

        joined_labels = "LABEL " + " ".join(labels)

        return joined_labels

    def create_docker_image_of_service(self,
                                       service: str = "api",
                                       image_namespace: str = "dracor",
                                       image_name: str = "stable-dracor",
                                       image_tag: str = None,
                                       commit_message: str = None,
                                       update_services: bool = True):
        """Create a Docker image of one of the services, normally the dracor-api container.

        Args:
            service (str, optional): Name of the service to create an image of. Defaults to "api", but could be
                any of self.__services.
            image_namespace (str, optional): Namespace the docker image will be added to. Defaults to "dracor".
            image_name (str, optional): Name of the image. Defaults to "stable-dracor"
            image_tag (str, optional): Tag of the image. This must be supplied if using dracor/stable-dracor.
                Defaults to id of the running system (not recommended to use).
            commit_message (str, optional): Commit message that will be used in the docker commit command.
            update_services (bool, optional): Replace the image in services with the newly created image.
                Defaults to True.
        """
        service_info = self.__services[service]
        logging.debug(f"Creating image of service '{service}'.")

        container_id = service_info["container"]
        containers = self.list_docker_containers()

        container_data = list(filter(lambda item: item["ID"] == container_id, containers))[0]
        # logging.debug(container_data)
        container_state = container_data["State"]
        logging.debug(f"Container {container_id} is in state: {container_state}.")

        if container_state == "running" and service == "api":
            logging.warning("The dracor-api container is running. There might be issues with the image, if it is"
                            " create from a running container. Consider stopping it before creating the image.")

        """
        # make a clean shutdown of the eXist-DB container
        # on shutting down the database with xmlrpc see https://exist-db.org/exist/apps/doc/devguide_xmlrpc
        import xmlrpc.client
        s = xmlrpc.client.ServerProxy('http://localhost:8080/exist/xmlrpc')
        s.shutdown()
        """

        # TODO: Must test with Capek thing if it causes problems when committing a running container

        if "image" in self.__services[service]:
            old_image = self.__services[service]["image"]
        else:
            old_image = None

        if image_tag is None:
            image_tag = self.__id

        new_image = f"{image_namespace}/{image_name}:{image_tag}"

        if commit_message is None:
            commit_message = "Create image with StableDraCor client"

        labels = self.__create_docker_image_labels(service=service,
                                                   base_image=old_image,
                                                   this_image=new_image)

        commit_operation = subprocess.run([
            "docker",
            "commit",
            "-m",
            f'"{commit_message}"',
            "-c",
            f"{labels}",
            container_id,
            new_image],
            capture_output=True)

        new_image_sha = commit_operation.stdout.decode("utf-8")

        self.__images_to_be_pushed.append(new_image)

        logging.info(f"Committed container {container_id} as {new_image}. Image identifier {new_image_sha}.")

        if update_services is True:
            self.__services[service]["image"] = new_image
            logging.debug(f"Updated services. Image {new_image} is set as service '{service}'.")

    def publish_docker_image(self,
                             user: str = None,
                             password: str = None,
                             logout: bool = True):
        """Push an image e.g. to Dockerhub
        Args:
            user (str, optional): Username on Dockerhub
            password (str, optional): Password on Dockerhub
            logout (bool, optional): Logout from docker after pushing the image
        """
        # docker login --username foo --password-stdin

        if user is not None and password is not None:
            password_bytes = bytes(password, "utf-8")
            login_operation = subprocess.run(
                ["docker", "login", "--username", f"{user}", "--password-stdin"], input=password_bytes, capture_output=True)
            logging.debug("Tried logging in to DockerHub: ")
            logging.debug(login_operation.stdout.decode("utf-8"))

        logging.debug(f"Following images will be pushed: {', '.join(self.__images_to_be_pushed)}.")

        for image in self.__images_to_be_pushed:
            push_operation = subprocess.run(["docker", "push", f"{image}"])

        logging.debug("Pushed images to DockerHub.")
        # reset
        self.__images_to_be_pushed = []

        if logout is True:
            logout_operation = subprocess.run(["docker", "logout"])
            logging.debug("Logged user out of Dockerhub.")

    def create_compose_file(self,
                            file_name: str = None):
        """Write the current configuration as a compose file

        Args:
            filename (str, optional): Overwrite the filename. Default will include self.__name if available, else
                self.__id.

        TODO: There is a lot of things hardcoded.. Better integrate self.__services and the compose file
        """
        compose_file = dict(
            services={}
        )

        for key in self.__services.keys():
            compose_file["services"][key] = {}
            compose_file["services"][key]["image"] = self.__services[key]["image"]

            # This is currently hardcoded, maybe this should fetch these parts from the running system?

            if key == "api":

                compose_file["services"][key]["environment"] = [
                    "DRACOR_API_BASE=http://localhost:8088/api",
                    "EXIST_PASSWORD ="
                ]

                compose_file["services"][key]["ports"] = [
                    "8080:8080"
                ]

                compose_file["services"][key]["depends_on"] = [
                    "triplestore",
                    "metrics"
                ]

            elif key == "metrics":

                compose_file["services"][key]["ports"] = [
                    "8030:8030"
                ]

            elif key == "frontend":

                compose_file["services"][key]["environment"] = [
                    "DRACOR_API=http://api:8080/exist/restxq"
                ]

                compose_file["services"][key]["ports"] = [
                    "8088:80"
                ]

                compose_file["services"][key]["depends_on"] = [
                    "api"
                ]

            elif key == "triplestore":
                compose_file["services"][key]["environment"] = [
                    "ADMIN_PASSWORD=qwerty"
                ]

                compose_file["services"][key]["ports"] = [
                    "3030:3030"
                ]

        if self.__name is not None:
            title = f"# Stable DraCor System '{self.__name}'"
        else:
            title = "# Stable DraCor System"

        if file_name is None:
            if self.__name is not None:
                file_name = f"compose.{self.__name}.yml"
            else:
                file_name = f"compose.{self.__id}.yml"

        with open(file_name, "w") as f:
            f.write(title)
            f.write("\n")
            yaml.dump(compose_file, f)
            logging.info(f"Stored configuration (docker-compose file) as {file_name}.")

    def get_api_info(self):
        """Should be able to load the info from the /info endpoint and store eXist-DB Version and API version.
        """
        return self.__api_get()

    def __corpus_exists(self, corpusname: str) -> bool:
        """Helper function to check if a corpus exists.
        The method checks if the provided identifier corpusname is in one of the fields "name" returned
        by the /corpora endpoint
        """
        logging.debug(f"Invoked __corpus_exists. Checking for corpora with name '{corpusname}'.")
        corpora = self.__api_get(method="corpora")
        result = list(filter(lambda corpus: corpusname in corpus["name"], corpora))
        if len(result) == 1:
            logging.debug(f"Corpus '{corpusname}' exists.")
            return True
        else:
            logging.debug(f"Corpus '{corpusname}' does not exist.")
            return False

    def add_corpus(self,
                   corpus_metadata: dict,
                   check: bool = True) -> bool:
        """Adds a corpus to the local instance.

            Documentation see https://dracor.org/doc/api#/admin/post-corpora

            Example of Corpus Metadata:
                {
                    "name": "rus",
                    "title": "Russian Drama Corpus",
                    "repository": "https://github.com/dracor-org/rusdracor"
                }

            This method does not register a corpus in self.__corpora. This needs to be done in the method calling this.

        Args:
            corpus_metadata (dict): Metadata of corpus to add.
            check (bool, optional): Check if corpus exists after adding it. Defaults to True.

        Returns:
            bool: True if successful.
        """
        logging.debug(f"Adding corpus {corpus_metadata['name']}.")

        response = self.__api_post(
            corpus_metadata,
            method="corpora",
            username=self.__username,
            password=self.__password)

        if response == 200:
            logging.debug(f"Request to add corpus was successful.")

            if check is True:
                logging.debug("Running check for metadata of local corpus.")
                local_corpus_meta = self.__api_get(corpusname=corpus_metadata['name'])

                errors = []
                for field in corpus_metadata.keys():
                    if field in local_corpus_meta:
                        if local_corpus_meta[field] != corpus_metadata[field]:
                            errors.append(field)
                    else:
                        logging.debug(f"Field {field} not in metadata of created corpus.")
                        errors.append(field)
                logging.debug(f"Checked fields of metadata: {str(len(errors))} values did not match.")
                if len(errors) == 0:
                    logging.info(f"Successfully created corpus {local_corpus_meta['name']}. All metadata is available "
                                 f"and plays are available.")
                    return True
                elif len(errors) == 1 and errors[0] == "dramas":
                    logging.info(f"Successfully created corpus {local_corpus_meta['name']}. All metadata is available. "
                                 f"Plays have not been added yet.")
                    return True
                else:
                    logging.warning(f"Created corpus, but metadata {str(len(errors))} fields do not match: "
                                    f"Fields {','.join(errors)} are different.")
                    return True

            else:
                logging.debug("Did not check if local corpus exists.")
                logging.info(f"Successfully created corpus {corpus_metadata['name']}.")
                return True

        elif response == 409:
            logging.warning(f"Did not add corpus {corpus_metadata['name']}. Corpus already exists.")
            return False

    def copy_corpus_contents(self,
                             source_api_url: str = None,
                             source_corpusname: str = None,
                             target_corpusname: str = None,
                             exclude: list = None):
        """Copy the contents of a corpus identified by source_corpusname into the local DraCor instance.
        It is expected that the corpus exists in the local instance. Corpus metadata is not copied from the source.

        Args:
            source_api_url (str, optional): Url of the API to copy from. Default is https://dracor.org
            source_corpusname (str): Identifier "corpusname" in the source system
            target_corpusname (str, optional): Identifier "corpusname" in the local system.
                Default will take the name of the source corpus.
            exclude (list, optional): List of playnames to ignore. Per default all plays will be included.
        """

        if source_api_url is None:
            # use default production
            source_api_url = self.__dracor_api_urls["production"]

        logging.debug(f"Copying corpus contents of {source_corpusname} from {source_api_url}.")

        # If not explicitly set, use the corpus name of the source
        if target_corpusname is None:
            logging.debug(f"Target corpus name not set explicitly, will use source name: {source_corpusname}.")
            target_corpusname = source_corpusname

        source_plays = api_get(api_base_url=source_api_url, corpusname=source_corpusname)["dramas"]
        logging.debug(f"Retrieved metadata of {str(len(source_plays))} plays from source.")

        errors = []
        success = []

        # Plays to exclude
        if exclude is not None:
            exclude = exclude
        else:
            exclude = []
            # there are plays excluded, need to record that in the self.__corpora

        for play in source_plays:
            if play["name"] in exclude:
                logging.debug(f"Play {play['name']} is excluded.")

                # register this in self.__corpora in the source
                self.__exclude_play_from_corpus_source(corpusname=target_corpusname,
                                                       source_name=source_corpusname,
                                                       id_type="slug",
                                                       id=play["name"])
            else:

                try:
                    logging.debug(f"Retrieving TEI of {play['name']}.")
                    tei = api_get(
                            api_base_url=source_api_url,
                            corpusname=source_corpusname,
                            playname=play["name"],
                            method="tei")

                    logging.debug(f"Storing TEI of {play['name']}.")

                    self.__api_put(
                            tei,
                            method="tei",
                            corpusname=target_corpusname,
                            playname=play["name"],
                            username=self.__username,
                            password=self.__password,
                            headers={"Content-Type": "application/xml"})

                    success.append(play['name'])

                except:
                    logging.warning(f"Could not add  {play['name']} to corpus f{target_corpusname}.")
                    errors.append(play["name"])

        logging.info(f"Added contents of corpus {source_corpusname} from {source_api_url}. "
                     f"{len(success)} plays were added.")

        # log the number of plays successfully added to the source
        self.__register_added_play_number_in_corpus_source(corpusname=target_corpusname,
                                                           source_name=source_corpusname,
                                                           num_of_plays=len(success))

        if exclude:
            logging.debug(f"Number of plays excluded: {len(exclude)}.")

        logging.debug(f"There were {len(errors)} Errors.")

    def __register_corpus(self,
                                corpusname: str = None,
                                source_name: str = None,
                                source_corpusname: str = None,
                                source_commit: str = None,
                                source_type: str = None,
                                source_url: str = None):
        """Helper Function to register a(n) (added) corpus in self.__corpora

        Args:
            corpusname (str): Identifier "corpusname" of the new corpus
            source_name (str, optional): Name of the source. Defaults to the value of source_corpusname.
            source_corpusname: (str, optional): Identifier "corpusname" of the source corpus
            source_commit (str, optional): Commit representing the state of a corpus added from GitHub
            source_type (str, optional): Type of the source.
                Typical values "api", "repository", "files" (from a local folder on hard disk)
            source_url (str, optional): URL of the source
        """

        if corpusname in self.__corpora:
            logging.debug(f"Corpus {corpusname} already registered in self.__corpora. "
                          f"No additional source has been added.")
            # TODO: decide if source will be added
        else:
            logging.debug(f"Registering corpus {corpusname} in self.__corpora.")
            self.__corpora[corpusname] = dict(
                corpusname=corpusname,
                timestamp=datetime.now().isoformat()
            )
            if source_name is not None or source_corpusname is not None:

                self.__corpora[corpusname]["sources"] = dict()

                source = dict()

                if source_type is not None:
                    source["type"] = source_type
                if source_corpusname is not None:
                    source["corpusname"] = source_corpusname
                if source_url is not None:
                    source["url"] = source_url
                if source_commit is not None:
                    source["commit"] = source_commit
                source["timestamp"] = datetime.now().isoformat()

                # is a source name is provided use this to identify the source,
                # otherwise use the source corpus name
                if source_name is not None:
                    self.__corpora[corpusname]["sources"][source_name] = source
                else:
                    self.__corpora[corpusname]["sources"][source_corpusname] = source
            else:
                logging.debug(f"No source provided for corpus {corpusname}.")

    def __register_added_play_number_in_corpus_source(self,
                                                      corpusname:str = None,
                                                      source_name: str = None,
                                                      num_of_plays: int = None):
        """Helper function to add a play count to a source of a corpus in self.__corpora

        Returns:

        """
        """
        __register_added_play_number_in_corpus_source(corpusname=target_corpusname,
                                                   source_name=source_corpusname,
                                                  num_of_plays=len(success))
        """
        assert corpusname in self.__corpora, f"No such corpus '{corpusname}' registered in self.__corpora."
        assert source_name in self.__corpora[corpusname]["sources"], f"Source {source_name} is not registered with " \
                                                                     f" corpus {corpusname} in self.__corpora."

        self.__corpora[corpusname]["sources"][source_name]["num_of_plays"] = num_of_plays

    def copy_corpus(self,
                    source_api_url: str = None,
                    source_corpusname: str = None,
                    metadata: dict = None,
                    copy_contents: bool = True,
                    exclude: list = None,
                    check: bool = True):
        """Copy a corpus identified by source_corpusname into the local DraCor instance. This method creates the local
        corpus and copies the metadata from the source. Metadata can be overwritten by metadata. This will selectively
        overwrite the fields, data is provided for. If a corpus shall be renamed, pass {"name": "xyz"},...

        Args:
            source_api_url (str, optional): URL of the API to copy the data from. If not set will use DraCor production
            source_corpusname (str): Identifier "corpusname" of the corpus to copy from source
            metadata (dict, optional): Metadata fields to overwrite. Can be used to change the name of a corpus.
            copy_contents (bool, optional): Add the contents of the source corpus. Defaults to True.
            exclude (list, optional): List of identifiers of plays in the source corpus to ignore.
            check (bool, optional): Check if corpus is available after trying to copy. Defaults to True.
        """

        if source_api_url is None:
            # use default production
            source_api_url = self.__dracor_api_urls["production"]

        assert source_corpusname is not None, "Providing a corpusname from the source corpus is mandatory."

        logging.debug(f"Copying corpus {source_corpusname} from {source_api_url}.")

        # retrieve the metadata from the source corpus, default is https://dracor.org
        logging.debug("Retrieving corpus metadata.")
        original_corpus_metadata = api_get(api_base_url=source_api_url, corpusname=source_corpusname)

        new_corpus_metadata = original_corpus_metadata
        if metadata:
            logging.debug(f"Partially overwrite metadata:")
            for field in metadata.keys():
                new_corpus_metadata[field] = metadata[field]
                logging.debug(f"Overwritten metadata field {field} of new corpus.")

        # add the corpus, if returned True, everything went well
        corpus_add_status = self.add_corpus(corpus_metadata=new_corpus_metadata)

        if corpus_add_status is False:
            logging.warning(f"Copying corpus {source_corpusname} failed.")
            return False
        else:
            # This registers an added corpus in self.__corpora (only the metadata and the source, not it's contents)
            self.__register_corpus(corpusname=new_corpus_metadata['name'],
                                   source_name=source_corpusname,
                                   source_corpusname=source_corpusname,
                                   source_type="api",
                                   source_url=f"{source_api_url}corpora/{source_corpusname}")

        if copy_contents:
            self.copy_corpus_contents(
                source_api_url=source_api_url,
                source_corpusname=source_corpusname,
                target_corpusname=new_corpus_metadata["name"],
                exclude=exclude)
                # Handling the excludes will be done with the copy_corpus_contents method

        if check is True:
            logging.debug(f"Checking if corpus {new_corpus_metadata['name']} is available.")
            try:
                local_corpus_data = self.__api_get(corpusname=new_corpus_metadata['name'])
                logging.debug(f"Retrieving corpus {new_corpus_metadata['name']} works.")
            except:
                return False
                logging.warning(f"Corpus {new_corpus_metadata['name']} is not available locally.")

            if copy_contents is True:
                logging.debug("Check if the number of plays are as expected:")
                original_play_count = len(original_corpus_metadata["dramas"])
                local_play_count = len(local_corpus_data["dramas"])
                if exclude is None:
                    expected_play_count = original_play_count
                else:
                    expected_play_count = original_play_count - len(exclude)
                logging.debug(f"Original play count: {str(original_play_count)}; "
                              f"Local play count: {str(local_play_count)}; "
                              f"Expected play count: {str(expected_play_count)}")

                if local_play_count == expected_play_count:
                    logging.info(f"Copying {original_corpus_metadata['name']} (as {new_corpus_metadata['name']}) was "
                                 f"successful. Plays (that were not excluded) were also copied entirely.")
                    return True
                else:
                    logging.warning("Corpus is available locally, but numbers of included plays are not as expected."
                                    "Not all requested plays could be copied. Check the logfile.")
                    return False
            else:
                logging.info(f"Copying {original_corpus_metadata['name']} metadata (as "
                             f"corpus {new_corpus_metadata['name']}) was successful. Plays were not copied.")
                return True

        else:
            logging.info(f"Copied corpus {source_corpusname} from {source_api_url}. Did not run a check.")
            return True

    def remove_corpus(self, corpusname: str = None):
        """Remove a corpus from the local instance"""

        assert corpusname, "Providing a corpusname is mandatory."

        logging.debug(f"Removing corpus {corpusname}")

        delete_status = self.__api_delete(corpusname=corpusname,
                                          username=self.__username,
                                          password=self.__password)
        if delete_status == 200:
            logging.info(f"Removed corpus {corpusname}.")
            # TODO: this should be reflected in self.__corpora
            return True

        if delete_status == 404:
            logging.warning(f"Could not remove corpus {corpusname}. No such corpus.")
            return False
        else:
            logging.debug(f"Server returned status code: {str(delete_status)}.")
            logging.info(f"Could not remove corpus {corpusname}.")
            False

    def remove_play_from_corpus(self,
                                corpusname: str = None,
                                playname: str = None):
        """Remove a play from a corpus

        Args:
            corpusname (str): Identifier "corpusname" the play is contained in.
            playname (str): Identifier "playname" of a play.
            TODO: could add check to see if play is removed?
        """
        assert corpusname is not None, "Providing a corpusname is mandatory."
        assert playname is not None, "Providing a playname is mandatory."

        remove_status = self.__api_delete(corpusname=corpusname, playname=playname)
        if remove_status == 200:
            logging.info(f"Removed play {playname} from corpus {corpusname}.")
            # TODO: this should be reflected in self.__corpora
            return True
        if remove_status == 404:
            logging.warning(f"No such play {playname} in {corpusname}.")
            return False
        else:
            logging.debug(f"Unknown error code returned by delete operation: {str(remove_status)}")
            return False

    def add_plays_from_directory(self,
                                 corpusname: str,
                                 directory: str,
                                 corpus_metadata: dict = None
                                 ):
        """Load local data and add it to a corpus identified by corpusnam.
        If the corpus does not exist, it will be created with minimal metadata.

        Args:
            corpusname (str): Identifier 'corpusname' of the corpus to add the plays to
            directory (str): Path to the local directory
            corpus_metadata (dict, optional): Metadata of the corpus to create
        """

        assert os.path.exists(directory), f"The directory {directory} does not exist."

        files = os.listdir(directory)
        logging.debug(files)

        logging.debug(f"Checking if corpus '{corpusname}' already exists.")
        corpus_exist = self.__corpus_exists(corpusname)

        if corpus_exist is False:
            logging.debug(f"Corpus '{corpusname}' does not exist. Need to create it.")

            if corpus_metadata:
                logging.debug("Corpus metadata is provided. Try to create the corpus with this metadata.")
                # if the method add_corpus returns True, the corpus has been created
                create_corpus_status = self.add_corpus(corpus_metadata)

                assert create_corpus_status is True, f"Could not create '{corpusname}' with provided metadata. " \
                                                     f"Plays can not be be loaded."

            else:
                logging.debug(f"No metadata provided for corpus."
                              f" Will create a corpus with the name '{corpusname}'")
                new_corpus_metadata = {"name": corpusname, "title": "No title provided."}
                self.add_corpus(corpus_metadata=new_corpus_metadata)

            # TODO: check if self.add_corpus registers a corpus
            # This registers an added corpus in self.__corpora (only the metadata and the source, not it's contents)
            # self.add_corpus doesn't do the registering; therefore we do it here
            # TODO: "folder" in "source_name" should be a save name of the directory path or something like that;
            # maybe a truncated hash of the path?
            # another (better) option would be to hash the files

            folder_content_string = ",".join(files)
            #logging.debug(folder_content_string)
            files_hashed = hashlib.sha1(folder_content_string.encode("UTF-8")).hexdigest()[:8]
            logging.debug(f"Registering corpus {corpusname}. Truncated hash of filenames in folder {directory} "
                          f"is: {files_hashed}")
            self.__register_corpus(corpusname=corpusname,
                                   source_name=files_hashed,
                                   source_type="files")

            assert self.__corpus_exists(corpusname) is True, f"Failed to create corpus {corpusname}."

        success = []
        errors = []

        for file in files:
            logging.debug(f"Importing {file} from directory {directory}.")
            import_flag = True

            filepath = directory + "/" + file
            if ".xml" in file:
                playname = file.split(".xml")[0]
            else:
                logging.debug("Maybe not an xml file according to the file extension.")
                import_flag = False

            # parsing the xml would not be necessary for import but this checks if the file is wellformed
            # otherwise the API would reject it but I am not sure, what the API would return as error code
            if import_flag is True:
                try:
                    xml = ET.parse(filepath)
                except ParseError:
                    logging.warning(f"File at '{filepath}' is not well-formed XML. Can not add '{file}'."
                                    f"Should also check if file extension is '.xml'!")
                    import_flag = False

            if import_flag is True:

                with open(filepath, "r") as f:
                    tei = f.read().encode("utf-8")
                    self.__api_put(
                        tei,
                        method="tei",
                        corpusname=corpusname,
                        playname=playname,
                        username=self.__username,
                        password=self.__password,
                        headers={"Content-Type": "application/xml"})

                success.append(file)
                logging.info(f"Added TEI data from file '{file}' to corpus '{corpusname}'.")

        if len(errors) == 0:
            logging.info(f"Imported {str(len(success))} files from {directory} as corpus '{corpusname}'.")
            return True
        else:
            logging.debug(f"Number of successful imports: {str(len(success))}.")
            logging.debug(f"Number of errors: {str(len(errors))}.")
            logging.debug(errors)
            return False

    def add_play_version_to_corpus(self,
                                   corpusname: str = None,
                                   playname: str = None,
                                   commit: str = None,
                                   filename: str = None,
                                   repository_name: str = None,
                                   repository_owner: str = "dracor-org",
                                   repository_data_folder: str = "tei",
                                   repository_blob_base_url: str = "raw.githubusercontent.com",
                                   protocol: str = "https",
                                   check: bool = True) -> bool:
        """Add a play in a certain version from a git repository defined by a git commit to a corpus.

        Args:
            corpusname (str, optional): Identifier 'corpusname' of the local target corpus. 
                If not set the mandatory repository_name will be used.
            playname (str, optional): Identifier 'playname' in the target corpus. This is the name, the play will get.
                If not set the mandatory filename will be used.
            commit (str, optional): Commit-ID identifying a Version of the data in the repository.
                If not set it will use the most recent data from the "main" branch.
            filename (str): File name of the file containing the play data. The file extension ".xml" will be added.
            repository_name (str): Name of the repository. This must not match the corpusname, e.g. "gerdracor".
            repository_owner (str): Username of the user owning the repository. Defaults to "dracor-org"
            repository_data_folder (str, optional): Path from the root folder of the repository to the folder containing 
                the files. Defaults to "tei"
            repository_blob_base_url (str): Base url to retrieve a blob/raw data from the repository. 
                Defaults to "raw.githubusercontent.com"
            protocol (str, optional): Protocol used in the request url. Defaults to "https"
            check (bool, optional): Additional check if the play has been successfully added. Defaults to True.

        TODO: This kind of addition is not reflected in self.__corpora. Register that.
        """

        assert repository_name is not None, "Providing the name of a repository (repository_name) is required."
        assert filename is not None, "Providing a file name (filename) is required."

        if commit is None:
            logging.debug(f"Commit not set, will try to use latest version of {filename} from main branch.")
            commit = "main"

        if filename.endswith(".xml"):
            checked_filename = filename
        else:
            checked_filename = f"{filename}.xml"

        source_url = f"{protocol}://{repository_blob_base_url}/{repository_owner}/{repository_name}/{commit}/" \
                     f"{repository_data_folder}/{checked_filename}"

        logging.debug(f"Fetching github data from source url: {source_url}")

        r = requests.get(url=source_url)
        if r.status_code == 200:
            import_flag = True
            tei = r.text.encode("utf-8")
            logging.debug(f"Could retrieve data from '{source_url}'.")
        else:
            import_flag = False
            logging.debug(f"Retrieving data from '{source_url}' failed. Server returned: {str(r.status_code)}.")

        # try to parse xml
        if import_flag is True:
            try:
                xml = ET.fromstring(tei)
                logging.debug("Could parse returned data. XML is well-formed.")
            except ParseError:
                logging.warning(f"File at url '{source_url}' is not well-formed XML. Can not add it to the database.")
                import_flag = False

        if corpusname is None:
            logging.debug(f"Name of the target corpus is not provided. "
                          f" Using the name of the repository '{repository_name}' as name of the corpus.")
            corpusname = repository_name

        if self.__corpus_exists(corpusname) is False:
            logging.debug(f"Must create corpus '{corpusname}'.")
            new_corpus_metadata = {"name": corpusname,
                                   "title": "Automatically generated corpus",
                                   "description": "This corpus has been created automatically "
                                                  "because it did not exist during an import operation."}
            self.add_corpus(corpus_metadata=new_corpus_metadata, check=False)

        if playname is None:
            playname = filename.replace(".xml", "")
            logging.debug(f"Identifier 'playname' of the play is not set. Will use filename '{filename}' as "
                          f" the identifier of the play: ('{playname}').")

        if import_flag is True:
            add_status = self.__api_put(
                tei,
                method="tei",
                corpusname=corpusname,
                playname=playname,
                username=self.__username,
                password=self.__password,
                headers={"Content-Type": "application/xml"})

            if add_status == 200:
                logging.debug("PUT request to add data was successful.")
            elif add_status == 404:
                logging.debug(f"PUT request not successful. Corpus {corpusname} probably "
                              f" does not exist. Can not add the data.")
                import_flag = False
            else:
                logging.debug(f"PUT request to add data was not successful. Status code. {add_status}.")
                import_flag = False

        if check is True and import_flag is True:
            logging.debug(f"Checking if play '{playname}' has been added to corpus '{corpusname}'.")
            added_play = self.__api_get(corpusname=corpusname, playname=playname)
            if type(added_play) == dict:
                logging.info(f"Play '{playname}' retrieved from '{source_url}' has been successfully added "
                             f"to corpus '{corpusname}'. Checked and found local play data.")
                return True
            else:
                logging.warning(f"Play from '{source_url}' has not been added.")
                return False
        elif import_flag is True and check is False:
            logging.info(f"Data of play '{playname}' retrieved from '{source_url}' most likely has been"
                         f" added to corpus '{corpusname}'. Did not run additional check.")
            return True
        elif import_flag is False:
            logging.warning(f"Could not add play from source '{source_url}'.")
            return False
        else:
            logging.debug("This else statement should not be reachable.")
            return False

    def __get_latest_commit_hash_in_github_repo(self,
                                                repository_name: str,
                                                repository_owner: str = "dracor-org") -> str:
        """Use the GitHUb API to get the commit-ID of the latest commit on a repository.
        The method will get Github commits by using /repos/{owner}/{name}/commits. We assume that the first entry in
        this list is the latest commit, but we have to tested it yet.

        For example, a commit hash is necessary to retrieve the tree and thus the files at a given point in time.

        Args:
            repository_owner (str, optional): User owning the repository. Defaults to "dracor-org"
            repository_name (str): Name of the repository.

        TODO: Investigate if the first returned commit is the latest commit indeed.
        """
        get_commits_api_call = f"repos/{repository_owner}/{repository_name}/commits"
        data = self.__github_api_get(api_call=get_commits_api_call)

        if data is not None:
            commit_data = data[0]
            commit_hash = commit_data["sha"]
            logging.debug(f"Retrieved latest (?) commit of repo '{repository_owner}/{repository_name}': {commit_hash}.")
            return commit_hash

    def list_plays_in_repo(self,
                                  commit: str = None,
                                  repository_name: str = None,
                                  repository_owner: str = "dracor-org",
                                  repository_base_url: str = "github.com",
                                  repository_data_folder: str = "tei"
                                  ):
        """List TEI-XML files of plays in a repository. This has been tested with GitHub only.

        Args:
            commit (str, optional): Commit-ID representing the state of the repository at a given point in time.
                If it is not set, the (probably) latest commit will be used.
            repository_name (str): Name of the repository
            repository_owner: Username of the user owning the repository. Defaults to "dracor-org"
            repository_base_url: Base of the repository. If it is the default "github.com", the Github API will be used.
            repository_data_folder: Path from root to folder containing the play data. Defaults to "tei"

        Returns:
            list: List containing the file names of plays included in the repo at a point in time identified by a commit
        """
        assert repository_name is not None, "Providing a repository name is mandatory!"

        if commit is None:
            logging.debug("No commit set. Getting latest commit.")
            commit = self.__get_latest_commit_hash_in_github_repo(repository_name=repository_name,
                                                                  repository_owner=repository_owner)
        if repository_base_url != "github.com":
            logging.critical(f"Not using Github. This is only implemented for the Github API. Will probably fail.")

        logging.debug(f"Using Github to get the commit {commit} and the tree object thereof.")
        get_commit_api_call = f"repos/{repository_owner}/{repository_name}/commits/{commit}"
        commit_data = self.__github_api_get(api_call=get_commit_api_call)
        tree = commit_data["commit"]["tree"]
        logging.debug(f"Got the Github tree of commit '{commit}': {tree['sha']} at url {tree['url']}.")

        if "/" in repository_data_folder:
            logging.critical(f"Getting data in nested directories is not implemented. Can only get the contents of"
                             f" a single data folder contained in the repository root.")

        # get the tree and then the hash of the tree of the sub-folder
        repository_root_folder = self.__github_api_get(url=tree["url"])

        # this is not the very best check in the world
        if type(repository_root_folder) == dict:
            if repository_root_folder["truncated"] is True:
                logging.warning("Not all items in the root folder of the repository are included in the response.")

            tree_objects_in_root_folder = repository_root_folder["tree"]
            data_folder_object = list(filter(lambda item: item["path"] == repository_data_folder,
                                             tree_objects_in_root_folder))[0]
            logging.debug(data_folder_object)
            logging.debug(f"Found data folder '{repository_data_folder}' in tree objects. "
                          f" sha: {data_folder_object['sha']}, url: {data_folder_object['url']}.")

        else:
            logging.warning(f"GET request to get the data '{repository_data_folder}' folder failed!")
            data_folder_object = None

        if data_folder_object is not None:
            logging.debug(f"Getting files in the data folder.")
            parsed_data_folder_tree_object = self.__github_api_get(url=data_folder_object["url"])

            # This is not the very best check in the world
            if type(parsed_data_folder_tree_object) == dict:

                if parsed_data_folder_tree_object["truncated"] is True:
                    logging.warning("The contents of the TEI folder are paged! Need to implement!")

                file_objects = parsed_data_folder_tree_object["tree"]
                logging.debug(f"Found {len(file_objects)} in the data folder tree.")

                filenames = []

                for item in file_objects:
                    # exclude directories
                    if item["type"] == "blob":
                        filenames.append(item["path"])

            else:
                logging.warning(f"GET request to retrieve the contents of the data folder failed.")
                filenames = []

            return filenames

    def __exclude_play_from_corpus_source(self,
                                          id: str = None,
                                          corpusname: str = None,
                                          source_name: str = None,
                                          id_type: str = "slug",
                                          ):
        """Helper function to exclude a play from a source of a corpus in self.__corpora

        Args:
            id (str): Identifier of the play, normally a slug. But type is set with "id_type".
            corpusname (str): Identifier "corpusname" that has a source of which the play was excluded
            source_name (str): Name of the source of the corpus ins self.__corpora
            id_type (str): Type of ID. Defaults to "slug", but can be "id" if it is a DraCor ID, e.g. "ger12345"
                Using anything else than slug is currently not recommended.
        TODO: this would need to be refactored. There is a really deeply nested if/else structure.
        """

        assert corpusname in self.__corpora, f"Identifier corpusname {corpusname} is not registered in self.__corpora"

        if "sources" in self.__corpora[corpusname]:
            if source_name in self.__corpora[corpusname]["sources"]:
                if "exclude" in self.__corpora[corpusname]["sources"][source_name]:
                    # check if excluding of same ID type
                    if "type" in self.__corpora[corpusname]["sources"][source_name]["exclude"]:
                        # check if excluding the same type
                        if self.__corpora[corpusname]["sources"][source_name]["exclude"]["type"] != id_type:
                            # TODO: decide if raise Exception here because this is bad.
                            logging.warning("Using different ID types to identify plays to exclude. This will "
                                            "cause problems!")
                        else:
                            # all fine, check if IDs already have been excluded
                            if "ids" in self.__corpora[corpusname]["sources"][source_name]["exclude"]:
                                self.__corpora[corpusname]["sources"][source_name]["exclude"]["ids"].append(id)
                            else:
                                logging.debug("Strangely everything is set, but no IDs are listed to be excluded.")
                                self.__corpora[corpusname]["sources"][source_name]["exclude"]["ids"] = [id]
                    else:
                        logging.warning("There might be something excluded before but the type of ID has not been set.")
                        self.__corpora[corpusname]["sources"][source_name]["exclude"]["type"] = id_type
                else:
                    # need to add exclude dictionary and the substructures because it is the first time a play
                    # is excluded from this source
                    self.__corpora[corpusname]["sources"][source_name]["exclude"] = dict()
                    self.__corpora[corpusname]["sources"][source_name]["exclude"]["type"] = id_type
                    self.__corpora[corpusname]["sources"][source_name]["exclude"]["ids"] = [id]
            else:
                logging.warning(f"Source with name '{source_name}' is not registered with the sources of the corpus "
                                f"{corpusname}.")

        else:
            logging.warning("Strangely there are not sources registered in the corpus.")

    def add_corpus_from_repo(self,
                             commit: str = None,
                             repository_name: str = None,
                             repository_owner: str = "dracor-org",
                             repository_base_url: str = "github.com",
                             repository_data_folder: str = "tei",
                             use_metadata_of_corpus_xml: bool = True,
                             corpus_metadata: dict = None,
                             exclude: list = None) -> bool:
        """Add a corpus from a repository

        Args:
            commit (str, optional): Commit-ID representing the state of the repository at a given point in time.
                If it is not set, the (probably) latest commit will be used.
            repository_name (str): Name of the repository
            repository_owner: Username of the user owning the repository. Defaults to "dracor-org"
            repository_base_url: Base of the repository. If it is the default "github.com", the Github API will be used.
            repository_data_folder (str, optional): Path to the folder containing the files. Defaults to "tei"
            use_metadata_of_corpus_xml (bool, optional): Use the file "corpus.xml" in the root folder for metadata.
            corpus_metadata (dict, optional): Metadata to overwrite corpus metadata with.
            exclude (list, optional): File names (without file extension .xml) of plays to exclude from new corpus.

        Returns:
            bool: True if successful
        TODO: There seems to be some issues when trying to add CzeDracor
        """
        assert repository_name is not None, "Providing a repository name is required!"

        if commit is None:
            logging.debug("No commit set. Getting latest commit.")
            commit = self.__get_latest_commit_hash_in_github_repo(repository_name=repository_name,
                                                                  repository_owner=repository_owner)

        if use_metadata_of_corpus_xml is True:
            logging.debug(f"Get the repository root folder tree at commit '{commit}'.")

            get_commit_api_call = f"repos/{repository_owner}/{repository_name}/commits/{commit}"
            commit_data = self.__github_api_get(api_call=get_commit_api_call)

            if type(commit_data) == dict:
                tree = commit_data["commit"]["tree"]
                logging.debug(f"Got the Github tree of commit '{commit}': {tree['sha']} at url {tree['url']}.")
            else:
                logging.debug(f"Getting the tree from GitHub was not successful.")
                tree = None

            if tree is not None:
                root_folder_tree_data = self.__github_api_get(url=tree["url"])

                if type(root_folder_tree_data) == dict:
                    items = root_folder_tree_data["tree"]
                    corpus_xml_object = list(filter(lambda item: item["path"] == "corpus.xml",
                                             items))[0]
                    # logging.debug(corpus_xml_object)

                    if corpus_xml_object["type"] == "blob":
                        corpus_xml_blob_url = corpus_xml_object["url"]
                        logging.debug(f"Found corpus.xml blob at {corpus_xml_blob_url}.")
                    else:
                        logging.debug(f"Could not find url of corpus.xml blob.")
                        corpus_xml_blob_url = None
                else:
                    logging.debug(f"Requesting the tree of the root folder was not successful.")
                    corpus_xml_blob_url = None

            if corpus_xml_blob_url is not None:
                # TODO: Continue here. Need to change to get_github_api stuff
                blob_data = self.__github_api_get(url=corpus_xml_blob_url)
                if "content" in blob_data:
                    corpus_xml_string = base64.b64decode(blob_data["content"])
                    corpus_xml = ET.fromstring(corpus_xml_string)
                else:
                    logging.warning(f"Could not decode and parse corpus.xml. Operation might fail.")
                    corpus_xml = None

            if corpus_xml is not None:
                ns = {"tei": "http://www.tei-c.org/ns/1.0"}
                logging.debug("Extracting corpus metadata from corpus.xml.")

                existing_corpus_metadata = {}

                corpus_title_e = corpus_xml.find("tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", ns)
                if corpus_title_e is not None:
                    corpus_title = corpus_title_e.text
                    existing_corpus_metadata["title"] = corpus_title
                    logging.debug(f"Title: {corpus_title}")

                corpus_name_e = corpus_xml.find("tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno[@type='URI']",
                                                ns)
                if corpus_name_e is not None:
                    corpus_name = corpus_name_e.text
                    existing_corpus_metadata["name"] = corpus_name
                    logging.debug(f"Corpusname: {corpus_name}")

                corpus_desc_elems = corpus_xml.findall("tei:teiHeader/tei:encodingDesc/tei:projectDesc/tei:p", ns)
                if len(corpus_desc_elems) != 0:
                    corpus_desc_texts = []
                    for elem in corpus_desc_elems:
                        corpus_desc_texts.append(elem.text)
                    corpus_desc_text = "".join(corpus_desc_texts)
                    existing_corpus_metadata["description"] = corpus_desc_text
                    logging.debug(f"Description: {corpus_desc_text}")
                    # TODO: this ignores included sub-elements, e.g. links

                # TODO: Extract other metadata, e.g. licence, licenceUrl, and whatnot

        if corpus_metadata is not None:
            logging.debug("Prepare corpus metadata for creating corpus.")

            if existing_corpus_metadata:
                logging.debug("Overwriting corpus.xml extracted data with the provided corpus metadata.")
                new_corpusmetadata = existing_corpus_metadata
            else:
                new_corpusmetadata = {}

            for key in corpus_metadata.keys():
                new_corpusmetadata[key] = corpus_metadata[key]

        elif existing_corpus_metadata is not None:
            new_corpusmetadata = existing_corpus_metadata

        else:
            logging.debug("Did not provide corpus metadata and not using corpus.xml.")
            new_corpusmetadata = {"name": repository_name,
                                  "title": "No title provided",
                                  "description": "Corpus was created automatically during import of corpus "
                                                 " repository from GitHub. The repository did not contain a"
                                                 " corpus.xml file with corpus metadata."}

        if "name" not in new_corpusmetadata:
            logging.debug(f"No identifier corpusname for target corpus supplied. Use name of source repository"
                          f" '{repository_name}'.")
            new_corpusmetadata["name"] = repository_name

        create_corpus_status = self.add_corpus(corpus_metadata=new_corpusmetadata, check=False)
        if create_corpus_status is True:
            # register the corpus self.__register_corpus()
            # This registers an added corpus in self.__corpora (only the metadata and the source, not it's contents)
            # self.add_corpus doesn't do the registering; therefore we do it here
            if "name" in existing_corpus_metadata:
                source_corpusname = existing_corpus_metadata["name"]
                source_name = source_corpusname
            else:
                logging.debug(f"There is no corpusname availabele for the source. Use the name of the repository "
                              f"'{repository_name}' as name of the source. This probably happend because corpus.xml "
                              f" could not be found and might cause further problems.")
                source_name = repository_name
                source_corpusname = None

            self.__register_corpus(corpusname=new_corpusmetadata["name"],
                                   source_corpusname=source_corpusname,
                                   source_name=source_name,
                                   source_type="repository",
                                   source_commit=commit,
                                   source_url=f"https://{repository_base_url}/{repository_owner}/{repository_name}")

        filenames = self.list_plays_in_repo(commit=commit,
                                            repository_owner=repository_owner,
                                            repository_name=repository_name,
                                            repository_base_url=repository_base_url,
                                            repository_data_folder=repository_data_folder)
        logging.debug(f"Got {len(filenames)} filenames from repo {repository_owner}/{repository_name}.")

        success = []
        errors = []

        if exclude is None:
            logging.debug("No plays are to be excluded.")
            exclude = []
        else:
            logging.debug(f"Should exclude {', '.join(exclude)}.")

        for filename in filenames:
            if filename in exclude or f"{filename}.xml" in exclude or filename.replace(".xml", "") in exclude:
                logging.debug(f"File {filename} is excluded.")
                if filename.endswith(".xml"):
                    slug = filename[:-4]
                else:
                    slug = filename

                # Exclude the file also from the source in self.__corpora
                self.__exclude_play_from_corpus_source(corpusname=new_corpusmetadata["name"],
                                                       source_name=source_name,
                                                       id_type="slug",
                                                       id=slug)
                pass
            else:
                # This is what normally happens if a file is not explicitly excluded
                add_file_status = self.add_play_version_to_corpus(
                    corpusname=new_corpusmetadata["name"],
                    commit=commit,
                    filename=filename,
                    repository_name=repository_name,
                    repository_owner=repository_owner)
                if add_file_status is True:
                    success.append(filename)
                else:
                    # There was an error with the file, need to exclude them in self.__corpora as well
                    errors.append(filename)
                    if filename.endswith(".xml"):
                        slug = filename[:-4]
                    else:
                        slug = filename

                    # Exclude the file also from the source in self.__corpora
                    self.__exclude_play_from_corpus_source(corpusname=new_corpusmetadata["name"],
                                                           source_name=source_name,
                                                           id_type="slug",
                                                           id=slug)

        # TODO: this might log a count to self.__corpora source; should use len(success)
        # TODO: should log the number of plays successfully added to the source
        self.__register_added_play_number_in_corpus_source(corpusname=new_corpusmetadata["name"],
                                                           source_name=source_name,
                                                           num_of_plays=len(success))

        if len(errors) == 0:
            logging.info(f"Successfully added all {len(success)} files to {new_corpusmetadata['name']}.")

            return True
        else:
            logging.warning(f"Added {len(success)} of {len(filenames)} to corpus {new_corpusmetadata['name']}."
                            f"{len(errors)} errors occurred. Files, that were not added: {', '.join(errors)}.")

            return False

    def list_dracor_github_repos(self):
        """List available Repositories of dracor-og on Github. This should allow for excluding
        repositories that don't have a corpus.xml file in the root directory and no folder "tei" containing xml files
        """
        raise Exception("Not implemented.")


