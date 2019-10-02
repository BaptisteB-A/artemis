from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("nb-corr-05")])
class NbCorr05(object):
    """
    TODO: put there comments about the dataset
    """

    def test_nb_corr_05_01(self):
        self.journey(
            _from="stop_area:NC5:SA:1",
            to="stop_area:NC5:SA:4",
            datetime="20041213T0700",
        )


@set_scenario({"nb-corr-05": {"scenario": "new_default"}})
class TestNbCorr05NewDefault(NbCorr05, ArtemisTestFixture):
    pass


@set_scenario({"nb-corr-05": {"scenario": "experimental"}})
class TestNbCorr05Experimental(NbCorr05, ArtemisTestFixture):
    pass
