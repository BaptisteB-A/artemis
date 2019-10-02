from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("test-03")])
class ArtTest03(object):
    """
    TODO: put there comments about the dataset
    """

    def test_art_test_03_01(self):
        self.journey(
            _from="stop_area:TS3:SA:1",
            to="stop_area:TS3:SA:6",
            datetime="20041214T0700",
        )


@set_scenario({"test-03": {"scenario": "new_default"}})
class TestTest03NewDefault(ArtTest03, ArtemisTestFixture):
    pass


@set_scenario({"test-03": {"scenario": "experimental"}})
class TestTest03Experimental(ArtTest03, ArtemisTestFixture):
    pass
