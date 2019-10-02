from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("mdi")])
class MDI(object):
    """
    TODO: put there comments about the dataset
    """

    def test_mdi_01(self):
        self.journey(
            _from="stop_area:MDI:SA:1",
            to="stop_area:MDI:SA:3",
            datetime="20070308T0700",
        )

    def test_mdi_02(self):
        self.journey(
            _from="stop_area:MDI:SA:1",
            to="stop_area:MDI:SA:4",
            datetime="20070308T0700",
        )

    def test_mdi_03(self):
        self.journey(
            _from="stop_area:MDI:SA:2",
            to="stop_area:MDI:SA:3",
            datetime="20070308T0700",
        )

    def test_mdi_04(self):
        self.journey(
            _from="stop_area:MDI:SA:2",
            to="stop_area:MDI:SA:1",
            datetime="20070419T0700",
        )


@set_scenario({"mdi": {"scenario": "new_default"}})
class TestMDINewDefault(MDI, ArtemisTestFixture):
    pass


@set_scenario({"mdi": {"scenario": "experimental"}})
class TestMDIExperimental(MDI, ArtemisTestFixture):
    pass
