import requests, json
from requests.auth import HTTPBasicAuth
import logging


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
        return r.text.encode('utf-8')
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
            password (str, optional): Password. Defaults to empty string ""
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


class StableDraCor:
    """Stable Local DraCor instance

    Attributes:
        api_base_url (str): URL of the local DraCor API
    """

    # URLs of external DraCor APIs
    __dracor_api_urls = dict(
        production="https://dracor.org/api/",
        staging="https://staging.dracor.org/api/",
    )

    # Default URL of a local Dracor instance
    api_base_url = "http://localhost:8088/api/"

    # Default credentials
    __username = "admin"
    __password = ""

    def __init__(self,
                 api_base_url: str = None,
                 username: str = None,
                 password: str = None):
        """

        Args:
             api_base_url (str, optional): URL of the local DraCor API. Default is set to http://localhost:8088/api/
             username (str, optional): Username of the local instance. Default is set to "admin"
             password (str, optional): Password of the admin user of the local instance. Default is set to ""
        """
        logging.debug("Initializing...")

        if api_base_url is not None:
            logging.debug(f"Update api_base_url with: {api_base_url}")
            self.api_base_url = api_base_url

        if username is not None:
            logging.debug(f"Update username with: {api_base_url}")
            self.__username = username

        if password is not None:
            logging.debug(f"Update password with: {api_base_url}")
            self.__password = password

        logging.debug("Initialized new instance of StableDraCor.")

    def __api_get(self, **kwargs):
        """Send GET request to running local instance. Uses the function api_get, but overrides api_base_url
        with the URL of the local instance"""
        return api_get(api_base_url=self.api_base_url, **kwargs)

    def __api_post(self, data, **kwargs):
        """Send POST request to running local instance. Uses the function api_post, but overrides api_base_url
        with the URL of the local instance

        Args:
            data: Payload to include in body

        """

        logging.debug(kwargs)
        return api_post(data, api_base_url=self.api_base_url, **kwargs)

    def __api_put(self, data, **kwargs):
        """Send PUT request to running local instance. Uses the function api_put, but overrides api_base_url
        with the URL of the local instance

        Args:
            data: Payload to include in body
        """
        logging.debug(kwargs)
        return api_put(data, api_base_url=self.api_base_url, **kwargs)

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
                    if local_corpus_meta[field] != corpus_metadata[field]:
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

        # Plays to exclude
        if exclude is not None:
            exclude = exclude
        else:
            exclude = []

        for play in source_plays:
            if play["name"] in exclude:
                logging.debug(f"Play {play['name']} is excluded.")
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

                except:
                    logging.warning(f"Could not add  {play['name']} to corpus f{target_corpusname}.")
                    errors.append(play["name"])

        logging.info(f"Added contents of corpus {source_corpusname} from {source_api_url}.")
        if exclude:
            logging.debug(f"Number of plays excluded: {len(exclude)}.")
        logging.debug(f"There were {len(errors)} Errors.")

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

        if copy_contents:
            self.copy_corpus_contents(
                source_api_url=source_api_url,
                source_corpusname=source_corpusname,
                target_corpusname=new_corpus_metadata["name"],
                exclude=exclude)

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
                    expected_play_count = original_play_count + len(exclude)
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



