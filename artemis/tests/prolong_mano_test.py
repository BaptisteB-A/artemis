from artemis.test_mechanism import ArtemisTestFixture, dataset, DataSet
import pytest
xfail = pytest.mark.xfail

@dataset([DataSet("prolong-mano")])
class TestProlongMano(ArtemisTestFixture):
    """
    TODO: put there comments about the dataset
    """
    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1123", raises=AssertionError)
    def test_prolong_mano_01(self):
        self.journey(_from="stop_area:PRM:SA:1",
                     to="stop_area:PRM:SA:5", datetime="20041213T0700")

    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1588", raises=AssertionError)
    def test_prolong_mano_02(self):
        self.journey(_from="stop_area:PRM:SA:1",
                     to="stop_area:PRM:SA:9", datetime="20041213T0700")
