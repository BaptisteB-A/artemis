"""
py test discover this file by default

Used to run some stuff at global scope
"""
import logging
import pytest
from artemis import utils
from artemis.configuration_manager import config
import requests
from retrying import retry
import ujson as json


def pytest_addoption(parser):
    """
    We add a pytest option to
    * skip the cities integration
    * skip the data integration (if it has been done before, it can save some time)
    """
    parser.addoption("--skip_cities", action="store_true", help="skip cities loading")
    parser.addoption("--skip_bina", action="store_true", help="skip binarization")
    parser.addoption(
        "--hard_journey_check",
        action="store_true",
        help="journeys comparison is made on full response",
    )
    parser.addoption(
        "--check_ref",
        action="store_true",
        help="only check that response is consistent with full response in reference files",
    )
    parser.addoption(
        "--create_ref",
        action="store_true",
        help="create a reference file using the response received - USE WITH CAUTION",
    )


class RetryError(Exception):
    pass


@pytest.fixture(scope="session", autouse=True)
def load_cities(request):
    """
    Load cities before running the tests
    """

    def is_retry_exception(exception):
        return isinstance(exception, RetryError)

    def get_last_cities_job():
        r_cities = requests.get(config["URL_TYR"] + "/v0/cities/status")
        r_cities.raise_for_status()
        return json.loads(r_cities.text)["latest_job"]

    @retry(stop_max_delay=300000, wait_fixed=500, retry_on_exception=is_retry_exception)
    def wait_for_cities_completion():
        """
        Wait until the 'cities' task is completed
        The task is considered failed if any error occurs while requesting Tyr
        """
        last_cities_job = get_last_cities_job()

        if last_cities_job and "state" in last_cities_job:
            if last_cities_job["state"] == "running":
                raise RetryError("Cities task still running...")
            elif last_cities_job["state"] == "failed":
                raise Exception("Job 'cities' status")
        else:
            raise Exception("Couldn't get 'cities' job status")

    log = logging.getLogger(__name__)
    if request.config.getvalue("skip_cities") or request.config.getvalue("check_ref"):
        log.info("skipping cities loading")
        return

    if config.get("USE_ARTEMIS_NG"):
        log.info("Posting cities")
        url = config["URL_TYR"] + "/v0/cities/"
        files = {"file": open(config["CITIES_INPUT_FILE"], "rb")}
        r = requests.post(url, files=files)
        r.raise_for_status()

        wait_for_cities_completion()
        log.info("Cities task finished")
        return

    log.info("loading cities database")

    utils.launch_exec(
        "cities -i {input} --connection-string".format(
            input=config["CITIES_INPUT_FILE"]
        ),
        additional_args=[config["CITIES_DB"]],
    )

    log.info("cities database loaded")
