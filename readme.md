*******
Artemis
*******

Business tests for Navitia

A new version of Artemis is now available. It allows Artemis to run locally (or on any machine) by running services in docker containers.
Follow the link to run [Artemis Next Generation](https://github.com/CanalTP/artemis/blob/master/artemis/readme.md)

Usage
=====

To run the test, run
``python -m py.test artemis/``
in the artemis dir

you can provide a custom config file (if the default_settings.py is not good enough for you) by providing a ``CONFIG_FILE`` environment variable

``CONFIG_FILE=my_conf.py python -m py.test artemis/``

There lot's of [other possible options](http://pytest.org/) that can be given to py.test. You can for example generate a junit like xml report with the ``--junit-xml=my_file.xml``.

There is also 4 custom artemis parameters:

 * --skip_cities: skip the loading of the cities database. It can save time when running several times artemis.
 WARNING the test will fail if the cities database is not loaded.

 * --skip_bina: skip the loading of the ED data. It can save lots of time when running several times artemis.
 WARNING the test will fail if the data are not loaded

 * --hard_journey_check: journey comparison is made using full response, not filtered one

 * --check_ref: only check that short response is consistent with full response in reference files (skip bina, cities and kraken calls)

Tests Organisation
==================

The tests are structured around data sets. Each dataset will be build to test a certain number of navitia fixtures (classic journey calls, over midnight journeys, ...).

Each data set is technically represented by a junit-like test fixture. The fixtures are implemented as class.
On the same data set lot's of different tests can be made. Each test will be modeled as a python method of the data set class.

Tests Mechanism
===============

Test setup
----------

The aim of Artemis is to test navitia.io, so the tested navitia architecture is as close to the production architecture as possible.

At the setup of test fixture (the dataset), the different services that have to be run will be launched (the statistics service, ``TYR``, ...)
and the data import process will be run. The ``Tyr`` service will be responsible for this (like in production).
 The only difference with the production architecture is that no data backup process will be done, thus ``Tyr`` do not move the data from the data directory.

Once the data import process is finished, the krakens will be poped. One kraken service will the launched for each data set needed for the test (we might want to test several dataset in the same fixture).

Apache is started after that to start the ``jörmungandr`` front end.

API call tests
--------------

Each api call in a test function will be stored as json and compared to a reference.
The comparison will be done only on a subset of the response field to limit the update of the tests references for minor api modifications.

If the api call is different than the reference the test is marked as in error and a user has to analyze the differences.
The user can then either correct the code if it is an error or update the reference if the new behavior is correct.

Test example
============

````python

@dataset([DataSet("paris"), DataSet("lyon")])
# --> the paris and the lyon data set will be used.
# --> it means that a paris and a lyon instance must have been installed
# --> must must thus have 2 data directory configured, 2 valid database and 2 kraken services: kraken_paris, kraken_lyon
class TestParisAndLyon(ArtemisTestFixture):
    # --> the test fixture. It has to have 'Test' at the begining or the end of its name
    # --> And it must inherit from ArtemisTestFixture

    """
    Mandatory: put there comments about the dataset
    what do we want to test, dataset construction, ...
    Those comment are very important for futures understanding of results differences
    """

    def test_classical_journey(self):
        #  --> one test on the data set
        #  --> The method must begin or end with 'test'
        """Optional, put there comment specific to the test case"""
        self.journey(_from="stop_area:AI1:SA:AIRPORTAIRPORT",
                     to="stop_area:AI1:SA:AIRPORTLYS", datetime="20120904T0700")

        # --> a call will be made the the journey API
        # --> this call will be saved as a json file and compared to the reference for this call
        # --> If there are important differences the test will be in error

    def test_over_midnight(self):
        res = self.journey(_from="stop_area:AI1:SA:AIRPORTAMS",
                     to="stop_area:AI1:SA:AIRPORTAIRPORT", datetime="20120904T0900")

        check_some_stuff(res)  # --> more custom python tests might be made

        add_diruptions()
        # --> some changes might be made to the environment
        # --> like adding disruptions, killing a service to test failure recovery, adding data, ...

        res2 = self.api("v1/stop_areas/bob/stop_points/")
        # --> we can now test another call to the API
        # --> this test will be checked against the reference as the first call

````
