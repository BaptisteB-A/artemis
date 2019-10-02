from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("nb-corr-04")])
class NbCorr04(object):
    """
    TODO: put there comments about the dataset
    """

    def test_nb_corr_04_01(self):
        self.journey(
            _from="stop_area:NC4:SA:1",
            to="stop_area:NC4:SA:4",
            datetime="20041213T0700",
        )

    def test_nb_corr_04_02(self):
        self.journey(
            _from="stop_area:NC4:SA:1",
            to="stop_area:NC4:SA:4",
            datetime="20041213T0700",
        )


@set_scenario({"nb-corr-04": {"scenario": "new_default"}})
class TestNbCorr04NewDefault(NbCorr04, ArtemisTestFixture):
    pass


@set_scenario({"nb-corr-04": {"scenario": "experimental"}})
class TestNbCorr04Experimental(NbCorr04, ArtemisTestFixture):
    pass
