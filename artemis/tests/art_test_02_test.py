from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("test-02")])
class ArtTest02(object):
    """
    TODO: put there comments about the dataset
    """

    def test_art_test_02_01(self):
        self.journey(
            _from="stop_area:TS2:SA:1",
            to="stop_area:TS2:SA:2",
            datetime="20041214T1100",
        )

    def test_art_test_02_02(self):
        self.journey(
            _from="stop_area:TS2:SA:1",
            to="stop_area:TS2:SA:3",
            datetime="20041214T1105",
        )

    def test_art_test_02_03(self):
        self.journey(
            _from="stop_area:TS2:SA:1",
            to="stop_area:TS2:SA:4",
            datetime="20041214T0700",
        )

    def test_art_test_02_04(self):
        self.journey(
            _from="stop_area:TS2:SA:3",
            to="stop_area:TS2:SA:4",
            datetime="20041214T0700",
        )


@set_scenario({"test-02": {"scenario": "new_default"}})
class TestArtTest02NewDefault(ArtTest02, ArtemisTestFixture):
    pass


@set_scenario({"test-02": {"scenario": "experimental"}})
class TestArtTest02Experimental(ArtTest02, ArtemisTestFixture):
    pass
