from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("freqgtfs")])
class FreqGtfs(object):
    """
    test frequencies to stops serialisation by FUSiO
    """

    def test_freqgtfs_01(self):
        self.journey(
            _from="stop_area:FQG:SA:35",
            to="stop_area:FQG:SA:1",
            datetime="20070417T054000",
        )

    def test_freqgtfs_02(self):
        self.journey(
            _from="stop_area:FQG:SA:35",
            to="stop_area:FQG:SA:1",
            datetime="20070417T050000",
        )

    def test_freqgtfs_03(self):
        self.journey(
            _from="stop_area:FQG:SA:35",
            to="stop_area:FQG:SA:1",
            datetime="20070417T010000",
        )

    def test_freqgtfs_04(self):
        self.journey(
            _from="stop_area:FQG:SA:35",
            to="stop_area:FQG:SA:1",
            datetime="20070417T052000",
            datetime_represents="arrival",
        )

    def test_freqgtfs_05(self):
        self.journey(
            _from="stop_area:FQG:SA:1",
            to="stop_area:FQG:SA:35",
            datetime="20070417T055000",
            datetime_represents="arrival",
        )


@set_scenario({"freqgtfs": {"scenario": "new_default"}})
class TestFreqGtfsNewDefault(FreqGtfs, ArtemisTestFixture):
    pass


@set_scenario({"freqgtfs": {"scenario": "experimental"}})
class TestFreqGtfsExperimental(FreqGtfs, ArtemisTestFixture):
    pass
