from artemis.test_mechanism import dataset, DataSet, set_scenario
from artemis.tests.fixture import ArtemisTestFixture


@dataset([DataSet("nb-corr-01")])
class NbCorr01(object):
    """
    TODO: put there comments about the dataset
    """

    def test_nb_corr_01_01(self):
        self.journey(
            _from="stop_area:NC1:SA:1",
            to="stop_area:NC1:SA:4",
            datetime="20041213T0700",
        )


@set_scenario({"nb-corr-01": {"scenario": "new_default"}})
class TestNbCorr01NewDefault(NbCorr01, ArtemisTestFixture):
    pass


@set_scenario({"nb-corr-01": {"scenario": "experimental"}})
class TestNbCorr01Experimental(NbCorr01, ArtemisTestFixture):
    pass
