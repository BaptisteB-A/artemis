from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture

# TODO: rename the test


@dataset([DataSet("boucle-01")])
class Boucle01(object):
    """
    TODO: put there comments about the dataset
    """

    def test_boucle_01_01(self):
        self.journey(
            _from="stop_area:BC1:SA:1",
            to="stop_area:BC1:SA:6",
            datetime="20041213T0730",
        )

    def test_boucle_01_02(self):
        self.journey(
            _from="stop_area:BC1:SA:3",
            to="stop_area:BC1:SA:7",
            datetime="20041213T0730",
            max_duration_to_pt=100,
        )

    def test_boucle_01_03(self):
        self.journey(
            _from="stop_area:BC1:SA:8",
            to="stop_area:BC1:SA:5",
            datetime="20041213T0730",
        )


@set_scenario({"boucle-01": {"scenario": "new_default"}})
class TestBoucle01NewDefault(Boucle01, ArtemisTestFixture):
    pass


@set_scenario({"boucle-01": {"scenario": "experimental"}})
class TestBoucle01Experimental(Boucle01, ArtemisTestFixture):
    pass
