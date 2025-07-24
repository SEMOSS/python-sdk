from typing import Any, List, Dict, Union, Optional, Set, Generator, Tuple
import requests
import json
import pandas as pd
import base64
import logging
from urllib.parse import urlparse, unquote
from pathlib import Path
import os

logger: logging.Logger = logging.getLogger(__name__)


class ServerClient:
    """ServerClient to make calls to a ai server instance

    Example:

    ```python
    >>> import ai_server

    # define access keys
    >>> loginKeys = {"secretKey":"<your_secret_key>","accessKey":"<your_access_key>"}

    # create connection object by passing in the secret key, access key and base url for the api
    >>> server_connection = ai_server.ServerClient(access_key=loginKeys['accessKey'], secret_key=loginKeys['secretKey'], base='<Your deployed server Monolith URL>')
    ```
    """

    # Class attribute to hold a singleton instance
    da_server = None

    def __init__(
        self,
        base: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        bearer_token_provider: Optional[str] = None,
    ) -> None:
        """
        Args:
            base (`str`):
                main url to access the server api
            access_key (`Optional[str]`):
                A user's access key is a unique identifier used for authentication and authorization. It will allow users or applications to access specific resources or perform designated actions within an ai-server instance.
            secret_key (`Optional[str]`):
                A user's confidential and securely stored piece of information that complements an access key, used in cryptographic processes to validate identity and ensure secure communication
            bearer_token (`Optional[str]`):
                A token provided from a successful login of a user to an existing IdP
            bearer_token_provider (`Optional[str]`):
                The existing IdP login type as recognized by the AuthProvider enum list
        """
        # set the base url as an instance attribute
        self.main_url: str = base

        if self.main_url is None or self.main_url == "":
            raise Exception("Must provide a valid URL for the running instance")

        if self.main_url.endswith(r"\/"):
            self.main_url = self.main_url[:-1]

        # set the access key as an instance attribute
        self.access_key: str = access_key
        # set the secret key as an instance attribute
        self.secret_key: str = secret_key
        # set the access key as an instance attribute
        self.bearer_token: str = bearer_token
        # set the secret key as an instance attribute
        self.bearer_token_provider: str = bearer_token_provider

        useUserAccessKey = (self.access_key is not None and self.access_key != "") and (
            self.secret_key is not None and self.secret_key != ""
        )
        useBearerToken = (
            self.bearer_token is not None and self.bearer_token != ""
        ) and (
            self.bearer_token_provider is not None and self.bearer_token_provider != ""
        )

        if not useUserAccessKey and not useBearerToken:
            raise Exception(
                "Must provide either access_key and secret_key for user access login or provide bearer_token and bearer_token_provider for login using your IdP access key"
            )

        # TODO provide definitons for all of these attributes
        # used to keep track of the authorization header after the user has authenticated
        self.auth_headers: Dict = {}
        if useUserAccessKey:
            self.loginUserAccessKey()
        else:
            self.loginBearerToken()

        # This will hold CSRF and any other required headers (merge into all calls)
        self.required_headers = {}

        # Perform CSRF/config logic (but don't crash if config fails)
        self.set_csrf_if_enabled()
        # keep track of the the insights created from this connection
        self.open_insights: Set = set()
        self.cur_insight: str = self.make_new_insight()

        # map to keep track of requests and responses outside of this class or in separate threads
        self.monitors = {}

        # set the instance of this class as the class attribute da_server
        ServerClient.da_server = self

    def loginUserAccessKey(self):
        """
        Register / validate the users secret & access key combination.

        Store the cookies to be used for other api calls after authentication
        """
        combined = self.access_key + ":" + self.secret_key
        combined_enc = base64.b64encode(combined.encode("utf-8"))
        headers = {"Authorization": f"Basic {combined_enc.decode('utf-8')}"}
        self.auth_headers: Dict = headers.copy()

        # make sure user is authenticated
        response, is_logged_in = self.is_session_login(self.auth_headers)
        if not is_logged_in:
            raise AuthenticationError("User could not successfully login")

        self.cookies = response.cookies
        # display the cookies
        logger.info(self.cookies)

    def loginBearerToken(self):
        """
        Register / validate the access key from an IdP

        Store the cookies to be used for other api calls after authentication
        """
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Bearer-Provider": self.bearer_token_provider,
        }
        self.auth_headers: Dict = headers.copy()

        # make sure user is authenticated
        response, is_logged_in = self.is_session_login(self.auth_headers)
        if not is_logged_in:
            raise AuthenticationError("User could not successfully login")

        self.cookies = response.cookies
        # display the cookies
        logger.info(self.cookies)

    def reconnect(self):
        self.logout()
        # Call __init__ to reconnect to the server on session timeout
        self.__init__(
            self.main_url,
            self.access_key,
            self.secret_key,
            self.bearer_token,
            self.bearer_token_provider,
        )

    def is_session_login(
        self, headers: Optional[Dict[str, str]] = None
    ) -> Tuple[Optional[requests.Response], bool]:
        """
        Check if user is logged in and return both the response and login status.

        Args:
            headers: Optional dictionary of HTTP headers to include in the request

        Returns:
            Tuple[Optional[Response], bool]: (response_object, is_logged_in)
        """
        config_url = self.main_url + "/config"
        try:
            response = requests.get(
                config_url, cookies=getattr(self, "cookies", None), headers=headers
            )
            response.raise_for_status()
            config_data = response.json()
            loginDetails = config_data.get("loginDetails")
            if loginDetails:
                return response, True
            else:
                return response, False
        except Exception as e:
            logger.error(f"Could not determine if user is logged in. Error: {str(e)}")
            return None, False

    def set_csrf_if_enabled(self):
        """
        Conditionally sets CSRF token for API requests based on server configuration.

        This method checks if CSRF protection is enabled on the server by fetching
        the configuration endpoint. If CSRF is enabled, it retrieves a CSRF token
        and adds it to the required headers for subsequent requests.

        The method performs the following steps:
        1. Fetches the server configuration from /config endpoint
        2. Checks if CSRF protection is enabled in the configuration
        3. If enabled, requests a CSRF token from /config/fetchCsrf endpoint
        4. Extracts the token from response headers and adds it to required_headers

        Attributes Modified:
            self.required_headers (dict): Updated with X-Csrf-Token header if CSRF is enabled

        Raises:
            requests.exceptions.HTTPError: If any HTTP request fails (status code >= 400)
            requests.exceptions.RequestException: For network-related errors
            ValueError: If the server response contains invalid JSON
            KeyError: If expected configuration keys are missing
        """
        config_url = self.main_url + "/config"
        try:
            resp = requests.get(config_url, cookies=getattr(self, "cookies", None))
            resp.raise_for_status()
            config_data = resp.json()
            use_csrf = config_data.get("csrf", False)
            if use_csrf:
                logger.info("CSRF enabled; fetching CSRF token.")
                csrf_headers = {
                    "x-csrf-token": "fetch",
                    "Accept": "application/json, text/plain, */*",
                }
                csrf_resp = requests.get(
                    self.main_url + "/config/fetchCsrf",
                    headers=csrf_headers,
                    cookies=getattr(self, "cookies", None),
                )
                csrf_resp.raise_for_status()
                csrf_token = csrf_resp.headers.get("X-Csrf-Token")
                if csrf_token:
                    self.required_headers["X-Csrf-Token"] = csrf_token
                    logger.info("CSRF token set.")
                else:
                    logger.warning("CSRF enabled but token not found in headers.")
            else:
                logger.info("CSRF not enabled; continuing without CSRF header.")
        except Exception as e:
            logger.error(f"Could not fetch or parse config for csrf. Error: {str(e)}")

    def get_auth_headers(self) -> Dict:
        """Get the autheroization headers used to authenticate the user"""
        return self.auth_headers

    def get_openai_endpoint(self) -> str:
        """Get the corrensponding openai endpoint for the CFG AI server"""
        return self.main_url + "/model/openai"

    def make_new_insight(self) -> str:
        """
        Create a new insight (temporal space) to operate within the ai-server at set it as the current insight.
        """
        _, is_logged_in = self.is_session_login()
        if not is_logged_in:
            return "Please login"

        response = requests.post(
            self.main_url + "/engine/runPixel",
            cookies=self.cookies,
            data={"expression": "META | true", "insightId": "new"},
            headers=self.required_headers,
        )

        # raise HTTP error if one occurs
        response.raise_for_status()

        json_output = response.json()
        self.cur_insight = json_output["insightID"]
        self.open_insights.add(self.cur_insight)

        return self.cur_insight

    def run_pixel(
        self,
        payload: str,
        insight_id: Optional[str] = None,
        full_response: Optional[bool] = False,
    ):
        """
        Send a pixel payload to the platforms /api/engine/runPixel endpoint.

        /api/engine/runPixel is the AI server's primary endpoint that consumes a flexible payload. The payload must contain two parameters, namely:
            1.) expression - The @payload passed is placed here and must comply and be defined in the Server's DSL (Pixel) which dictates what action should be taken
            2.) insightId - the temporal workspace identifier which isoloates the actions being performed

        Args:
            payload (`str`): DSL (Pixel) instruction on what specific action should be performed
            insight_id (`str`): Unique identifier for the temporal worksapce where actions are being isolated. Options are:
                - insight_id = '' -> Creates a temporary one time insight created but is not stored /     cannot be referenced for future state
                - insight_id = 'new' -> Creates a new insight which can be referenced in the same sesssion
                - insight_id = '<uuid/guid string>' -> Uses an existing insight id that exists in the user session
            full_response (`bool`): Indicate whether to return the full json response or only the actions output

        Returns:
            `Union[Any, Dict]`: The output object from the runPixel response or the entire runPixel response.
        """
        _, is_logged_in = self.is_session_login()
        if not is_logged_in:
            return "Please login"

        if insight_id is None:
            insight_id = self.cur_insight
            if insight_id is None:
                self.cur_insight = self.make_new_insight()
                insight_id = self.cur_insight

        pixel_payload = {"expression": payload, "insightId": insight_id}
        headers = self.required_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

        response = requests.post(
            self.main_url + "/engine/runPixel",
            cookies=self.cookies,
            data=pixel_payload,
            headers=headers,
        )

        response_dict = response.json()
        if "ERROR" in response_dict["pixelReturn"][0]["operationType"]:
            raise Exception(response_dict["pixelReturn"][0]["output"])

        if full_response:
            return response_dict
        else:
            return self.get_pixel_output(response_dict)

    def run_pixel_async(
        self, payload: str, insight_id: Optional[str] = None
    ) -> Union[Any, dict]:
        """
        Send a pixel payload to the platforms /api/engine/runPixelAsync endpoint.

        /api/engine/runPixelAsync is the AI server's primary endpoint that consumes a flexible payload. The payload must contain two parameters, namely:
            1.) expression - The @payload passed is placed here and must comply and be defined in the Server's DSL (Pixel) which dictates what action should be taken
            2.) insightId - the temporal workspace identifier which isoloates the actions being performed

        Args:
            payload (`str`): DSL (Pixel) instruction on what specific action should be performed
            insight_id (`str`): Unique identifier for the temporal worksapce where actions are being isolated. Options are:
                - insight_id = '' -> Creates a temporary one time insight created but is not stored /     cannot be referenced for future state
                - insight_id = 'new' -> Creates a new insight which can be referenced in the same sesssion
                - insight_id = '<uuid/guid string>' -> Uses an existing insight id that exists in the user session

        Returns:
            `Union[Any, Dict]`: The output object from the runPixelAsync containing the jobId
        """
        _, is_logged_in = self.is_session_login()
        if not is_logged_in:
            return "Please login"

        if insight_id is None:
            insight_id = self.cur_insight
            if insight_id is None:
                self.cur_insight = self.make_new_insight()
                insight_id = self.cur_insight

        pixel_payload = {"expression": payload, "insightId": insight_id}
        headers = self.required_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

        response = requests.post(
            self.main_url + "/engine/runPixelAsync",
            cookies=self.cookies,
            data=pixel_payload,
            headers=headers,
        )

        response_dict = response.json()
        return response_dict.get("jobId")

    def get_partial_responses(self, job_id: str) -> Generator:
        """
        Make continuous post requests to the partial endpoint until we see a change in the message state
        Args:
            job_id (`str`): The identifier of the job being run
        Returns:
            `Generator`: A generator that can be iterated through to get partials
        """

        if not job_id:
            raise ValueError("Job ID must be provided to get partial responses.")

        started_streaming = False
        terminal_statuses = {
            "ProgressComplete",
            "Complete",
            "Error",
            "UnknownJob",
            "Canceled",
        }

        while True:
            response = requests.post(
                url=self.main_url + "/engine/partial",
                cookies=self.cookies,
                data={"jobId": job_id},
                headers=self.required_headers,
            ).json()

            msg = response.get("message", {})
            status = response.get("status")
            new_chunk = msg.get("new", "")

            if new_chunk:
                if not started_streaming:
                    started_streaming = True
                yield new_chunk
            elif started_streaming and status in terminal_statuses:
                break
            elif status in {"Error", "UnknownJob", "Canceled"}:
                raise RuntimeError(f"Stream failed or canceled. Status: {status}")

    def get_pixel_output(self, response: Dict) -> Union[Any, List]:
        """
        Utility method to grab the output of runPixel call.

        Args:
            response (`Dict`): The runPixel response from the Tomcat Server

        Returns:
            `Union[Any, List]`: The output object or a list of objects
        """
        main_output = response["pixelReturn"][0]["output"]

        if isinstance(main_output, list):
            output = main_output[0]
        else:
            output = main_output

        return output

    def logout(self) -> None:
        """Closes the connection to the server."""
        requests.get(self.main_url + "/logout/all", cookies=self.cookies)
        self.cookies = None  # reset the connection attributes for the class

    def send_request(self, payload_struct: Dict) -> None:
        """
        Constructs the pixel payload from a PayloadStruct for various server resources such as ModelEngine, StorageEngine and DatabaseEngine

        Args:
            payload_struct (`dict`): the actual payload being sent to the AI Server

        Returns:
            `None`
        """

        # this is a synchronous call
        # but I dont want to bother the server proxy and leave it as is
        epoc = payload_struct["epoc"]

        input_payload_message = json.dumps(payload_struct, ensure_ascii=False)

        logger.info("Sending a PayloadStruct " + input_payload_message)

        # RemoteEngineRun is responsible for handling ModelEngine, StorageEngine and DatabaseEngine via ServerClient
        output_payload_message = self.run_pixel(
            payload='RemoteEngineRun(payload="<e>' + input_payload_message + '</e>");',
            insight_id=payload_struct["insightId"],
        )

        if epoc in self.monitors:
            self.monitors[epoc] = output_payload_message

    def get_open_insights(self) -> List[str]:
        """
        Retrieves a list of insight IDs created after establishing the connection.
        Args:
        Returns:
            `List[str]`: List of insight IDs
        """
        # MyOpenInsights is pre0defined server level reactor to handle the action of getting the insightIds
        open_insights = self.run_pixel(payload="MyOpenInsights();")

        # keep track of the open insights within the python object itself
        self.open_insights = set(open_insights)

        # return a list of insight ids
        return open_insights

    def drop_insights(self, insight_ids: Union[str, List[str]]) -> None:
        """
        Utility method to close insight(s). By default, if the the current/working insight is closed, then we will attempt to set to the first insight in open_insights as the current insight
        Args:
            insight_ids (`str` | `list`): a single insight or a list of insights the user wishes to close
        Returns:
            `None`
        """
        if isinstance(insight_ids, list):
            for id in insight_ids:
                self.run_pixel(insight_id=id, payload="DropInsight();")
                self.open_insights.discard(id)
        else:
            self.run_pixel(insight_id=insight_ids, payload="DropInsight();")
            self.open_insights.discard(insight_ids)

        if self.cur_insight not in self.open_insights:
            if len(self.open_insights) > 0:
                self.cur_insight = self.open_insights[0]
            else:
                self.cur_insight = None

    def import_data_product(
        self, project_id: str, insight_id: str, sql: str
    ) -> Union[pd.DataFrame, None]:
        """
        Accesses data within a saved insight (data product) via a REST API.

        Args:
        project_id (`str`):
            Given project/app unique identifier
        insight_id (`str`):
            Shared insight indentifier.
        sql (`bool`):
            SQL statement that is executable on the frames within the data product

        Returns:
          `pd.DataFrame` Pandas Dataframe based on the SQL statement passed in
        """
        base_url = (
            self.main_url
            + "/project-"
            + project_id
            + "/jdbc_json?insightId="
            + insight_id
            + "&open=true&sql="
        )

        dataProductUrl = base_url + sql
        response = requests.get(dataProductUrl, cookies=self.cookies).json()

        try:
            return pd.DataFrame(response["dataArray"], columns=response["columns"])
        except:
            try:
                return pd.DataFrame(response["data"], columns=response["columns"])
            except:
                return None

    def upload_files(
        self,
        files: List[str],
        project_id: Optional[str] = None,
        insight_id: Optional[str] = None,
        path: Optional[str] = None,
    ) -> List[str]:
        """
        Uploads files from the local device to the server.

        Args:
            files (`List[str]`):
                List of file paths to upload from local device
            insight_id (Optional[`str`]):
                Unique identifier for the temporal worksapce where actions are being isolated
            project_id (Optional[`str`]):
                Given project/app unique identifier
            path (Optional[`str`]):
                Specific upload path

        Returns (`List[str]`):
            List of file names that have been successfully uploaded
        """
        if not files:
            raise Exception("Must provide atleast one file to upload")

        # .../Monolith/api/uploadFile/baseUpload?insightId=de43ce0d-db2e-4ab9-a807-336bb86c4ea0&projectId=4c14bc58-973f-4293-87ed-a5d32c24f418&path=version/assets/
        if isinstance(files, str):
            files = [files]

        param = ""
        path = path or ""

        if insight_id or project_id or path:
            if insight_id == None:
                insight_id = self.cur_insight

            param += f"insightId={insight_id}"

            if project_id:
                if param:
                    param += "&"
                param += f"projectId={project_id}"

            if path:
                if param:
                    param += "&"
                param += f"path={path}"
        else:
            param += f"insightId={self.cur_insight}"

        param = f"?{param}"

        upload_post_request = f"{self.main_url}/uploadFile/baseUpload{param}"

        logger.info("The upload url is " + upload_post_request)

        insight_file_paths = []
        for filepath in files:
            with open(filepath, "rb") as fobj:
                response = requests.post(
                    upload_post_request,
                    cookies=self.cookies,
                    files={"file": fobj},
                    headers=self.required_headers,
                )
                insight_file_paths.append(response.json()[0]["fileName"])

        return insight_file_paths

    def download_file(
        self,
        file: str,
        project_id: Optional[str] = None,
        insight_id: Optional[str] = None,
        custom_filename: str = None,
    ) -> str:
        """
        Download files from the server to the local device.

        Args:
            file (`str`):
                The file path on the server to download
            insight_id (Optional[`str`]):
                Unique identifier for the temporal worksapce where actions are being isolated
            project_id (Optional[`str`]):
                Given project/app unique identifier
            custom_filename (Optional[`str`]):
                A custom filename for the download

        Returns (`str`):
            The file name that was downloaded
        """
        if not file:
            raise Exception("Must provide a file to download")

        # Construct the pixel statement
        project_param = ""
        if project_id is not None and project_id != "":
            project_param = ",space=[{project_id}]"

        download_asset_pixel = f"DownloadAsset(filePath=['{file}']{project_param})"
        download_file_key = self.run_pixel(
            payload=download_asset_pixel, insight_id=insight_id
        )

        insight_param = ""
        if insight_id:
            insight_param = insight_id
        else:
            insight_param = self.cur_insight

        download_get_url = f"{self.main_url}/engine/downloadFile?insightId={insight_param}&fileKey={download_file_key}"

        # Make the GET request
        response = requests.get(download_get_url, cookies=self.cookies, stream=True)
        response.raise_for_status()

        # Determine filename
        if custom_filename:
            filename = custom_filename
        else:
            filename = get_filename_from_url(
                download_get_url, response.headers, Path(file).name
            )

        # Get unique filename to avoid overwriting
        unique_filename = get_unique_filename(filename)

        # Download and save the file
        with open(unique_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)

        logger.info(f"File downloaded successfully: {unique_filename}")
        return unique_filename


def get_filename_from_url(url, headers=None, default_name=None):
    """Extract filename from URL or Content-Disposition header"""
    # First try to get filename from Content-Disposition header
    if headers and "Content-Disposition" in headers:
        content_disp = headers["Content-Disposition"]
        if "filename=" in content_disp:
            filename = content_disp.split("filename=")[1].strip("\"'")
            return unquote(filename)

    # Fall back to extracting from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # If no filename in path, use a default
    if not filename or "." not in filename:
        filename = default_name

    return unquote(filename)


def get_unique_filename(filename):
    """Generate a unique filename by appending (2), (3), etc. if file exists"""
    if not os.path.exists(filename):
        return filename

    # Split filename and extension
    path = Path(filename)
    name = path.stem
    suffix = path.suffix

    counter = 2
    while True:
        new_filename = f"{name} ({counter}){suffix}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1


class AuthenticationError(Exception):
    pass
