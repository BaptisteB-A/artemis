from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture
import pytest

xfail = pytest.mark.xfail


@dataset([DataSet("airport")])
class Airport(object):
    """
    TODO: put there comments about the dataset
    """

    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1485", raises=AssertionError)
    def test_airport_01(self):
        self.journey(
            _from="stop_area:AIR:SA:AIRPORTAIRPORT",
            to="stop_area:AIR:SA:AIRPORTLYS",
            datetime="20120904T0700",
        )

    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1485", raises=AssertionError)
    def test_airport_02(self):
        self.journey(
            _from="stop_area:AIR:SA:AIRPORTAMS",
            to="stop_area:AIR:SA:AIRPORTAIRPORT",
            datetime="20120904T0900",
        )

    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1485", raises=AssertionError)
    def test_airport_03(self):
        self.journey(
            _from="stop_area:AIR:SA:AIRPORTAIRPORT",
            to="stop_area:AIR:SA:AIRPORTCLY",
            datetime="20120908T1000",
        )

    def test_airport_04(self):
        self.journey(
            _from="stop_area:AIR:SA:AIRPORTAIRPORT",
            to="stop_area:AIR:SA:AIRPORTMRS",
            datetime="20120908T1200",
        )


@set_scenario({"airport": {"scenario": "new_default"}})
class TestAirportNewDefault(Airport, ArtemisTestFixture):
    pass


@set_scenario({"airport": {"scenario": "experimental"}})
class TestAirportExperimental(Airport, ArtemisTestFixture):
    pass
