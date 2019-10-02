import os
import ujson as json
import requests
import difflib
import sys
import six
import pytest
import logging
from collections import OrderedDict
import docker
import tarfile
import zipfile
import datetime
from retrying import retry
from artemis import default_checker, utils
from artemis.configuration_manager import config
from artemis.common_fixture import CommonTestFixture
from artemis.instance_default_values import default_values

from typing import List

if six.PY3:  # case using python 3
    from enum import Enum

elif six.PY2:  # case using python 2
    from aenum import Enum


class Colors(Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    PINK = "\033[95m"
    DEFAULT = "\033[0m"


logger = logging.getLogger(__name__)


def print_color(line, color=Colors.DEFAULT):
    """console print, with color"""
    sys.stdout.write("{}{}{}".format(color.value, line, Colors.DEFAULT.value))


class ArtemisTestFixture(CommonTestFixture):

    dataset_binarized = []  # type: List[str]

    @pytest.fixture(scope="function", autouse=True)
    def before_each_test(self, request):
        """
        setup function called before each test

        Note: py.test does not want to collect class with custom constructor,
        so we init the class in the setup
        """

        # Count how many times request_compare() is called within a test function
        # Needed for retrieving the correct reference file
        # (cf common_fixture.py get_reference_filename_prefix)
        self.nb_call_to_request_compare = 0

        self.check_ref = request.config.getvalue("check_ref")
        self.create_ref = request.config.getvalue("create_ref")

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def manage_data(cls, request):
        skip_bina = request.config.getvalue("skip_bina")
        if skip_bina:
            logger.info("Skipping binarisation...")
            return

        for data_set in cls.data_sets:
            if data_set.name in cls.dataset_binarized:
                logger.info(
                    "binarization dataset {} has been done, skipping....".format(
                        data_set
                    )
                )
                continue
            cls.update_instance_db(data_set.name)
            cls.remove_data_by_dataset(data_set)
            cls.update_data_by_dataset(data_set)
            cls.check_values(data_set.name)
            cls.dataset_binarized.append(data_set.name)

    @classmethod
    def update_instance_db(cls, data_set):
        """
        Update db with default values from migrations
        """
        # wait 1 min for Tyr task to update coverage
        @retry(
            stop_max_delay=60000,
            wait_fixed=500,
            retry_on_exception=utils.is_retry_exception,
        )
        def wait_for_tyr_instance_scan(instance_name):
            instances_url = "{base_url}/v0/instances/".format(
                base_url=config["URL_TYR"]
            )
            instances_request = requests.get(instances_url)
            instances_request.raise_for_status()
            if instance_name not in [
                instance["name"] for instance in json.loads(instances_request.text)
            ]:
                raise utils.RetryError(
                    "Instance {} not yet scanned by Tyr".format(instance_name)
                )

        wait_for_tyr_instance_scan(data_set)

        instance_url = "{base_url}/v0/instances/{instance}".format(
            base_url=config["URL_TYR"], instance=data_set
        )

        # Send request to update values
        r = requests.put(
            instance_url,
            data=json.dumps(default_values),
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()

    @classmethod
    def check_values(cls, data_set):
        """
        Security check: verify that db instance is updated with default values
        """
        _response, _, _status = utils.request(
            "coverage/{cov}/status".format(cov=data_set)
        )
        if _status != 200:
            raise Exception("Error while getting coverage status")

        cov_status = _response.get("status", {}).get("status", "")
        if cov_status != "running":
            raise Exception("Coverage {} NOT RUNNING".format(data_set))

        params = _response.get("status", {}).get("parameters", "")
        diffs = {}
        for k, v in default_values.items():
            if k not in params:
                diffs[k] = "Missing in Tyr"
            elif params[k] != v:
                diffs[k] = "{artemis} != {tyr}".format(artemis=v, tyr=params[k])
        if diffs:
            raise Exception("Diff(s) in parameters : {}".format(json.dumps(diffs)))

    @classmethod
    def remove_data_by_dataset(cls, data_set):
        file_path = "/srv/ed/output/{}.nav.lz4".format(data_set.name)
        logger.info("path to volume from container: " + file_path)
        containers = [
            x
            for x in docker.DockerClient(version="auto").containers.list()
            if "tyr_worker" in x.name
        ]
        if not containers:
            logger.error("No Docker Container found for tyr_worker")
        else:
            containers[0].exec_run("rm " + file_path)

    @classmethod
    def update_data_by_dataset(cls, data_set):
        def get_last_coverage_loaded_time(cov):
            _response, _, _ = utils.request("coverage/{cov}/status".format(cov=cov))
            return _response.get("status", {}).get("last_load_at", "")

<<<<<<< HEAD
        @retry(
            stop_max_delay=data_set.reload_timeout.total_seconds() * 1000,
            wait_fixed=data_set.fixed_wait.total_seconds() * 1000,
            retry_on_exception=utils.is_retry_exception,
        )
        def wait_for_data_processing(data_type, time_limit):
            """
            Wait until the data passed to Tyr is processed by checking the associated dataset state in the job
            :param data_type: Type of data passed to Tyr
            :param time_limit: UTC time from when the job could have been created. Allows to exclude jobs from previous bina
            :return: When dataset is "done"
            """
            instance_jobs_url = "{base_url}/v0/jobs/{instance}".format(
                base_url=config["URL_TYR"], instance=data_set
            )
            r = requests.get(instance_jobs_url)
            r.raise_for_status()
            jobs_resp = json.loads(r.text)["jobs"]
            for job in jobs_resp:
                job_creation = datetime.datetime.strptime(
                    job["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
                )
                if job_creation > time_limit:
                    for dataset in job["data_sets"]:
                        if data_type == dataset["type"]:
                            if dataset["state"] == "done":
                                logger.info("Dataset '{}' done!".format(data_type))
                                return
                            elif dataset["state"] != "failed":
                                raise utils.RetryError(
                                    "Job with dataset '{type}' still in process ({state})".format(
                                        type=data_type, state=job["state"]
                                    )
                                )
                            else:
                                raise Exception(
                                    "Dataset '{type}' in state '{state}'".format(
                                        type=data_type, state=job["state"]
                                    )
                                )
            raise utils.RetryError(
                "Job with dataset '{}' not yet created ".format(data_type)
            )

        @retry(
            stop_max_delay=data_set.reload_timeout.total_seconds() * 1000,
            wait_fixed=data_set.fixed_wait.total_seconds() * 1000,
            retry_on_exception=utils.is_retry_exception,
        )
=======
        # wait 5 min at most
        @retry(stop_max_delay=300000, wait_fixed=500)
>>>>>>> Pre-commit black passed
        def wait_for_kraken_reload(last_data_loaded, cov):
            new_data_loaded = get_last_coverage_loaded_time(cov)

            if last_data_loaded == new_data_loaded:
                raise utils.RetryError("kraken data is not loaded")

            logger.info("Kraken reloaded")

        data_path = config["DATA_DIR"]
        input_path = "{}/{}".format(config["CONTAINER_DATA_INPUT_PATH"], data_set.name)

        logger.info("updating data for {}".format(data_set.name))

        # opening the container as client
        containers = [
            x
            for x in docker.DockerClient(version="auto").containers.list()
            if "tyr_worker" in x.name
        ]
        if not containers:
            logger.error("No Docker Container found for tyr_worker")
        else:
            containers[0].exec_run("mkdir " + input_path)

        # Have the last reload time by Kraken
        last_reload_time = get_last_coverage_loaded_time(cov=data_set.name)

        def put_data(data_type, file_suffix, zipped):
            path = "{}/{}/{}".format(data_path, data_set.name, data_type)
            zip_file = "{}/{}_{}.zip".format(path, data_set.name, data_type)

            if os.path.exists(path):
                logger.info("putting {} data : {}".format(data_type, path))
                # get all the files names
                files = [f for f in os.listdir(path) if f.endswith(file_suffix)]

                if zipped:
                    # put them into a zip
                    with zipfile.ZipFile(zip_file, "w") as zip:
                        for f in files:
                            zip.write("{}/{}".format(path, f), arcname=f)

                # put the zip into a tar
                with tarfile.open("./{}.tar".format(data_type), "w") as tar:
                    if zipped:
                        tar.add(zip_file, arcname="{}.zip".format(data_type))
                    else:
                        for f in files:
                            tar.add("{}/{}".format(path, f), arcname=f)

                # send the tar to the volume
                with open("./{}.tar".format(data_type), "rb") as f:
                    containers[0].put_archive(input_path, f.read())
                    return True
            else:
                logger.warning("{} path does not exist : {}".format(data_type, path))
<<<<<<< HEAD

            return False

        # Get current datetime to check jobs created from now
        current_utc_datetime = datetime.datetime.utcnow()

        # List of tuples representing (type of data files, type of dataset, files extension, is zipped)
        data_to_process = [
            ("fusio", "fusio", (".txt", ".csv"), True),
            ("osm", "osm", ".pbf", False),
            ("fusio-poi", "poi", ".txt", True),
            ("geopal", "geopal", ".txt", True),
            ("fusio-geopal", "geopal", ".txt", True),
        ]

        dataset_types_to_process = []
        for data_files_type, dataset_type, file_ext, is_zipped in data_to_process:
            if put_data(data_files_type, file_ext, is_zipped):
                dataset_types_to_process.append(dataset_type)

        for dataset_type in dataset_types_to_process:
            wait_for_data_processing(dataset_type, current_utc_datetime)
=======

        # put the fusio data
        put_data("fusio", ".txt", zipped=True)
        # put the osm data
        put_data("osm", ".pbf", zipped=False)

        # put the poi data
        put_data("poi", ".txt", zipped=True)
        put_data("fusio-poi", ".txt", zipped=True)

        # put the geopal data
        put_data("geopal", ".txt", zipped=True)
        put_data("fusio-geopal", ".txt", zipped=True)
        put_data("fusio-address", ".txt", zipped=True)
>>>>>>> Pre-commit black passed

        # Wait until data is reloaded
        wait_for_kraken_reload(last_reload_time, data_set.name)

    @classmethod
    def kill_the_krakens(cls):
        for data_set in cls.data_sets:
            logger.debug("Restarting the Kraken {}".format(data_set.name))
            containers = [
                x
                for x in docker.DockerClient(version="auto").containers.list()
                if data_set.name in x.name
            ]
            if not containers:
                logger.error(
                    "No Docker Container found for Kraken {}".format(data_set.name)
                )
            else:
                containers[0].restart()

    @classmethod
    def pop_krakens(cls):
        """
        Does nothing.
        Inherited from old Artemis where the kraken is stopped then started
        In Artemis NG, the kraken is restarted in 'kill_the_krakens'
        """
        pass

<<<<<<< HEAD
    def request_compare(self, http_query, checker):
        self.nb_call_to_request_compare += 1
=======
    @retry(stop_max_delay=25000, wait_fixed=500)
    def get_last_rt_loaded_time(self, cov):
        _res, _, status_code = utils.request("coverage/{cov}/status".format(cov=cov))

        if status_code == 503:
            raise Exception("Navitia is not available")

        return _res.get("status", {}).get("last_rt_data_loaded", object())

    @retry(stop_max_delay=60000, wait_fixed=500)
    def wait_for_rt_reload(self, last_rt_data_loaded, cov):
        logging.warning(
            "waiting for rt reload later than {}".format(last_rt_data_loaded)
        )
        rt_data_loaded = self.get_last_rt_loaded_time(cov)

        if last_rt_data_loaded == rt_data_loaded:
            raise Exception("real time data not loaded")
        logger.info("RT data reloaded at {}".format(rt_data_loaded))

    def request_compare(self, url):
        # creating the url
        self.query = (
            config["URL_JORMUN"] + "/v1/coverage/" + str(self.data_sets[0]) + "/" + url
        )
>>>>>>> Pre-commit black passed

        # Get the json answer of the request (it is just a string here)
        http_response = requests.get(http_query)

        response_string = http_response.text

        if self.create_ref:
            # Create the reference file
            self.create_reference(http_query, response_string, checker)
        else:
            # Comparing my response and my reference
            self.compare_with_ref(http_query, response_string, checker)

    def api(self, url, response_checker=default_checker.default_checker):
        """
        Call to an endpoint using a coverage
        NOTE: works only when one region is loaded for the moment (when needed change this)
        """
        coverage_query = "/coverage/{coverage_name}/{query}".format(
            coverage_name=str(self.data_sets[0]), query=url
        )
        return self._api_call(coverage_query, response_checker)

    def _api_call(self, url, response_checker):
        """
        call the api and check against previous results

        the query is written in a file
        """
<<<<<<< HEAD
        http_query = "{base_query}/v1{url}".format(
            base_query=config["URL_JORMUN"], url=url
        )
        self.request_compare(http_query, response_checker)
=======
        self.request_compare(url)
>>>>>>> Pre-commit black passed

    def journey(
        self,
        _from,
        to,
        datetime,
        datetime_represents="departure",
        first_section_mode=[],
        last_section_mode=[],
        forbidden_uris=[],
        direct_path_mode=[],
        **kwargs
    ):
        """
        This function is coming from the test_mechanism.py file.
        We only use the part that generates the url.
        Other parts are calling test that fail because we do not have the whole navitia running.
        Thus, we do not need the "self" parameter, and response_checker is set to None.
        We have also added parts of other functions into it.
        Therefore, we only need to call journey and all the test are done from inside.
        """

        # Creating the URL with all the parameters for the query
        assert datetime
        query = "from={real_from}&to={real_to}&datetime={date}&datetime_represents={represent}".format(
            date=datetime, represent=datetime_represents, real_from=_from, real_to=to
        )
        for mode in first_section_mode:
            query = "{query}&first_section_mode[]={mode}".format(query=query, mode=mode)

        for mode in last_section_mode:
            query = "{query}&last_section_mode[]={mode}".format(query=query, mode=mode)

        for mode in direct_path_mode:
            query = "{query}&direct_path_mode[]={mode}".format(query=query, mode=mode)

        for uri in forbidden_uris:
            query = "{query}&forbidden_uris[]={uri}".format(query=query, uri=uri)

        for k, v in six.iteritems(kwargs):
            query = "{query}&{k}={v}".format(query=query, k=k, v=v)

        # Override scenario
        if self.__class__.data_sets[0].scenario in [
            "distributed",
            "experimental",
            "asgard",
        ]:
            overridden_scenario = "distributed"
        else:
            overridden_scenario = "new_default"
        query = "{query}&_override_scenario={scenario}".format(
            query=query, scenario=overridden_scenario
        )

<<<<<<< HEAD
        # Add current_datetime for disruptions
        query = "{query}&_current_datetime={d}".format(query=query, d=datetime)

        # creating the full URL
        http_query = "{base_url}/v1/coverage/{coverage}/journeys?{query_parameters}".format(
            base_url=config["URL_JORMUN"],
            coverage=str(self.data_sets[0]),
            query_parameters=query,
        )
        # launching request dans comparing
        self.request_compare(http_query, default_checker.default_journey_checker)

    def write_full_response_to_file(
        self,
        http_query,
        response_string,
        filepath,
        response_checker=default_checker.default_journey_checker,
    ):
        reference_text = OrderedDict()
        reference_text["query"] = http_query.replace(
            config["URL_JORMUN"][7:], "localhost"
        )
        reference_text["response"] = response_checker.filter(
            json.loads(response_string)
        )
        reference_text["full_response"] = json.loads(
            response_string.replace(config["URL_JORMUN"][7:], "localhost")
        )

        with open(filepath, "w") as ref:
            ref.write(
                json.dumps(
                    reference_text,
                    indent=2,
                    escape_forward_slashes=False,
                    encode_html_chars=False,
                    ensure_ascii=True,
                )
            )

    def create_reference(
        self,
        http_query,
        response_string,
        response_checker=default_checker.default_journey_checker,
=======
        # launching request dans comparing
        self.request_compare("journeys?" + query)

    def create_reference(
        self, response_checker=default_checker.default_journey_checker
>>>>>>> Pre-commit black passed
    ):
        """
        Create the reference file of a test using the response received.
        The file will be created in the git references folder provided in the settings file
        """
        # Check that the file doesn't already exist
<<<<<<< HEAD
        filepath = self.get_reference_file_path()
=======
        filename = self.get_file_name()
        filepath = os.path.join(config["REFERENCE_FILE_PATH"], filename)
>>>>>>> Pre-commit black passed

        if os.path.isfile(filepath):
            logger.warning(
                "NO REF FILE CREATED - {} is already present".format(filepath)
            )
<<<<<<< HEAD
            assert False
        else:
            self.write_full_response_to_file(
                http_query, response_string, filepath, response_checker
            )
            logger.info("Created reference file : {}".format(filepath))

    def compare_with_ref(self, http_query, response_string, response_checker):
=======
        else:
            # Concatenate reference file info
            reference_text = OrderedDict()
            reference_text["query"] = self.query.replace(
                config["URL_JORMUN"][7:], "localhost"
            )
            logger.warning("Query: {}".format(self.query))
            reference_text["response"] = response_checker.filter(
                json.loads(self.full_resp)
            )
            reference_text["full_response"] = json.loads(
                self.full_resp.replace(config["URL_JORMUN"][7:], "localhost")
            )

            # Write reference file directly in the references folder
            with open(filepath, "w") as ref:
                ref.write(json.dumps(reference_text, indent=4))
            logger.info("Created reference file : {}".format(filepath))

    def compare_with_ref(
        self, response, response_checker=default_checker.default_journey_checker
    ):
>>>>>>> Pre-commit black passed
        """
        Compare the response (which is a dictionary) to the reference
        First, the function retrieves the reference then filters both ref and resp
        Finally, it compares them
        """

<<<<<<< HEAD
        def print_diff(ref_file, resp_file, test_name):
=======
        def ref_resp2files(output_file, output_json):
            """
            Create a file for the filtered response and for the filtered reference
            """
            with open(output_file, "w") as reference_text:
                reference_text.write(output_json)

        def print_diff(ref_file, resp_file):
>>>>>>> Pre-commit black passed
            """
            Print differences between reference and response in console
            """
            # open reference
            with open(ref_file) as reference_text:
                reference = reference_text.readlines()
            # open response
            with open(resp_file) as response_text:
                response = response_text.readlines()

            # Print failed test name
<<<<<<< HEAD
            print_color("\n\n" + str(test_name) + " failed :" + "\n\n", Colors.PINK)
=======
            print_color("\n\n" + str(file_name) + " failed :" + "\n\n", Colors.PINK)
>>>>>>> Pre-commit black passed

            symbol2color = {"+": Colors.GREEN, "-": Colors.RED}
            for line in difflib.unified_diff(reference, response):
                print_color(line, symbol2color.get(line[0], Colors.DEFAULT))

        resp_dict = json.loads(response_string)

        # Filtering the answer. (We compare to a reference also filtered with the same filter)
        filtered_response = response_checker.filter(resp_dict)

<<<<<<< HEAD
        # Get the reference
        reference_filepath = self.get_reference_file_path()
=======
        # Create the file name
        filename = self.get_file_name()
        filepath = os.path.join(config["REFERENCE_FILE_PATH"], filename)
>>>>>>> Pre-commit black passed

        assert os.path.isfile(reference_filepath), "{} is not a file".format(
            reference_filepath
        )

<<<<<<< HEAD
        with open(reference_filepath, "r") as f:
=======
        with open(filepath, "r") as f:
>>>>>>> Pre-commit black passed
            raw_reference = f.read()

        # Transform the string into a dictionary
        ref_dict = json.loads(raw_reference)

        # Get only the full_response part from the ref
<<<<<<< HEAD
        reference_full_response = ref_dict["full_response"]
=======
        ref_full_response = dict_ref["full_response"]
>>>>>>> Pre-commit black passed

        # Filtering the reference
        filtered_reference = response_checker.filter(reference_full_response)

        # Compare response and reference
        try:
            response_checker.compare(filtered_response, filtered_reference)
        except AssertionError as e:
            # print the assertion error message
            logging.error("Assertion Error: %s" % str(e))
            # find name of test
<<<<<<< HEAD
            filename_prefix = self.get_reference_filename_prefix()

            # get output directory path
            output_dir_path = os.path.join(
                config["RESPONSE_FILE_PATH"], self.get_reference_suffix_path()
            )

            # create the directory if it does not exists
            if not os.path.exists(output_dir_path):
                os.makedirs(output_dir_path)

            # write response file
            response_filename = "{}_resp.json".format(filename_prefix)
            response_filepath = os.path.join(output_dir_path, response_filename)
            self.write_full_response_to_file(
                http_query, response_string, response_filepath, response_checker
            )

            # write reference file
            output_reference_filename = "{}_ref.json".format(filename_prefix)
            output_reference_filepath = os.path.join(
                output_dir_path, output_reference_filename
            )

            with open(output_reference_filepath, "w") as reference_text:
                reference_text.write(raw_reference)

            if six.PY3:
                from artemis import pytest_report_makers

                report_message = pytest_report_makers.journeys_diff(
                    filtered_reference, filtered_response
                )
                pytest_report_makers.add_to_report(
                    self.get_test_name(), http_query, report_message
                )
=======
            file_name = filename.split("/")[-1]
            file_name = file_name[:-5]

            # create a folder
            dir_path = config["RESPONSE_FILE_PATH"]
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # create path to ref and resp
            full_file_name_ref = dir_path + "/reference_" + file_name + ".txt"
            full_file_name_resp = dir_path + "/response_" + file_name + ".txt"

            json_filtered_reference = json.dumps(filtered_reference, indent=4)
            json_filtered_response = json.dumps(filtered_response, indent=4)

            # Save resp and ref as txt files in folder named outputs
            ref_resp2files(full_file_name_ref, json_filtered_reference)
            ref_resp2files(full_file_name_resp, json_filtered_response)

>>>>>>> Pre-commit black passed
            # Print difference in console
            # print_diff(response_filepath, output_reference_filepath, self.get_test_name())

            raise
