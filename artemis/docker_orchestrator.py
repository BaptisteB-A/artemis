import os
import subprocess
import docker
import requests
import yaml
import jinja2
import pytest
from retrying import retry
from artemis.configuration_manager import config

from docopt import docopt

COMPOSE_PROJECT_NAME = "navitia"


def get_compose_containers_list():
    """
    :return: a list of all containers created with docker-compose
    """
    all_containers_list = docker.DockerClient(version="auto").containers.list(all)
    return list(
        x for x in all_containers_list if COMPOSE_PROJECT_NAME in x.attrs["Name"]
    )


@retry(stop_max_delay=3000000, wait_fixed=2000)
def wait_for_jormun():
    query = config["URL_JORMUN"] + "/v1/status"
    response = requests.get(query)
    if response.status_code == 200:
        print(" -> JORMUN Responding")
    else:
        raise Exception("JORMUN NOT Responding")


@retry(stop_max_delay=3000000, wait_fixed=2000)
def wait_for_cities_db():
    print("Wait for cities db upgrade...")
    query = config["URL_TYR"] + "/v0/cities/status"
    response = requests.get(query)
    if response.status_code != 200:
        raise Exception("Cities not reachable")
    else:
        print(" -> Cities Responding")


# Unused for now!
@retry(stop_max_delay=3000000, wait_fixed=2000)
def wait_for_cities_job_completion():

    print("Wait for cities job completion...")
    query = config["URL_TYR"] + "/v0/cities/status"
    response = requests.get(query)
    if response.status_code != 200:
        raise Exception("Cities not reachable")
    else:
        last_job = response.text["latest_job"]
        if "state" not in last_job:
            raise Exception("Cities db job not created yet")
        elif last_job["state"] == "running":
            raise Exception("Cities db job in progress")
        else:
            print("cities job done!")


@retry(stop_max_delay=3000000, wait_fixed=2000)
def wait_for_kraken_stop(kraken_name):
    docker_list = get_compose_containers_list()
    kraken_container = next((x for x in docker_list if kraken_name in x.name), None)
    if kraken_container:
        if kraken_container.status == "running":
            raise Exception("Kraken still running...")
        else:
            print(
                "Container {} : Status: {}".format(
                    kraken_container.name, kraken_container.status
                )
            )
    else:
        print("No container found for {}".format(kraken_name))


def wait_for_docker_removal(kraken_name):
    print("Waiting to stop and remove {}".format(kraken_name))

    @retry(stop_max_delay=3000000, wait_fixed=2000)
    def wait_for_kraken_removal():
        docker_list = get_compose_containers_list()
        if next((x for x in docker_list if kraken_name in x.name), None):
            raise Exception("Kraken not yet removed...")

    wait_for_kraken_removal()


def init_dockers():
    """
    Run docker containers with no instance
    Create 'jormungandr' and 'cities' db
    """
    upCommand = "TAG=dev docker-compose -f docker-compose.yml -f kirin/docker-compose_kirin.yml -f asgard/docker-compose_asgard.yml up -d --remove-orphans"
    subprocess.Popen(upCommand, shell=True)
    wait_for_cities_db()


def launch_coverages(coverages):
    if not config["DOCKER_COMPOSE_PATH"]:
        raise Exception("DOCKER_COMPOSE_PATH needs to be set")
    instances_path = os.path.join(config["DOCKER_COMPOSE_PATH"], "artemis/")
    instances_list = os.path.join(instances_path, "artemis_custom_instances_list.yml")
    if not config["TEST_PATH"]:
        raise Exception("TEST_PATH needs to be set")
    test_path = config["TEST_PATH"]

    # Load instance Jinja2 template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config["DOCKER_COMPOSE_PATH"])
    )
    try:
        template = env.get_template("docker-instances.jinja2")
    except jinja2.TemplateNotFound:
        print("ERROR: Couldn't find template")
        return

    # Read the yaml file to get instances
    with open(instances_list, "r") as stream:
        data = yaml.load(stream)

        if coverages:
            list_of_coverages = []
            for coverage_to_run in coverages:
                list_of_coverages.extend(
                    [x for x in data["instances"] if coverage_to_run in x]
                )
        else:
            list_of_coverages = data["instances"]

        for instance in list_of_coverages:
            print("-> Instance read :\n {}".format(instance))
            # Create file for docker-compose
            instance_name = list(instance)[0]
            instance_file_name = "docker-instance-" + instance_name + ".yml"
            instance_file = os.path.join(instances_path, instance_file_name)
            print("Create : {}".format(instance_file))

            with open(instance_file, "w") as docker_instance:
                instance_render = [instance_name]
                kraken_env_parameters = (
                    instance[instance_name]["kraken_env"]
                    if "kraken_env" in instance[instance_name]
                    else []
                )
                jormun_env_parameters = (
                    instance[instance_name]["jormun_env"]
                    if "jormun_env" in instance[instance_name]
                    else ""
                )
                docker_instance.write(
                    template.render(
                        instances=instance_render,
                        kraken_env=kraken_env_parameters,
                        jormun_env=jormun_env_parameters,
                    )
                )

            # Create and start containers
            kraken_name = "kraken-" + instance_name
            upInstanceCommand = "TAG=dev docker-compose -f docker-compose.yml -f kirin/docker-compose_kirin.yml -f asgard/docker-compose_asgard.yml -f {} up -d --remove-orphans {} instances_configurator".format(
                instance_file, kraken_name
            )
            print("Run : {}".format(upInstanceCommand))
            subprocess.Popen(upInstanceCommand, shell=True)
            # Wait for the containers to be ready
            wait_for_jormun()

            test_class = instance[instance_name]["test_class"]
            # Run pytest
            pytest_cmd = test_path + " -k " + test_class

            print(
                "\n ----> RUN TESTS for {} \n     - CMD : {}\n".format(
                    instance_name, pytest_cmd
                )
            )
            pytest.main([test_path, "-k", test_class])
            print("\nTests Done!!!\n")

            # Delete instance container
            # The command is divided in 2 separate commands to be handled on old versions of docker/docker-compose
            stopCommand1 = "TAG=dev docker-compose -f docker-compose.yml -f kirin/docker-compose_kirin.yml -f asgard/docker-compose_asgard.yml -f {} stop {}".format(
                instance_file, kraken_name
            )
            subprocess.Popen(stopCommand1, shell=True)
            print("Run : {}".format(stopCommand1))
            wait_for_kraken_stop(kraken_name)

            stopCommand2 = "TAG=dev docker-compose -f docker-compose.yml -f kirin/docker-compose_kirin.yml -f asgard/docker-compose_asgard.yml -f {} rm -f {}".format(
                instance_file, kraken_name
            )
            subprocess.Popen(stopCommand2, shell=True)
            print("Run : {}".format(stopCommand2))
            wait_for_docker_removal(kraken_name)

            # Delete docker-compose instance file
            print("Remove instance file {}".format(instance_file))
            os.remove(instance_file)


def docker_clean():
    """
    Stop and remove all containers
    """
    print("Cleaning...")

    @retry(stop_max_delay=3000000, wait_fixed=2000)
    def wait_for_containers_stop():
        if get_compose_containers_list():
            raise Exception("Containers still running...")

    # Stop and remove containers
    downCommand = "TAG=dev docker-compose -f docker-compose.yml -f kirin/docker-compose_kirin.yml  -f asgard/docker-compose_asgard.yml down -v --remove-orphans"
    subprocess.Popen(downCommand, shell=True)

    wait_for_containers_stop()


script_doc = """ Artemis Docker Orchestrator.
Usage:
    docker_orchestrator.py test [<coverage>...]
    docker_orchestrator.py clean

Options:
    -h  --help  Help (obviously...)
"""
if __name__ == "__main__":
    args = docopt(script_doc, version="0.0.1")

    if args["test"]:
        os.chdir(config["DOCKER_COMPOSE_PATH"])

        init_dockers()

        launch_coverages(args["<coverage>"])

    if args["clean"] or args["test"]:
        docker_clean()
