from artemis.test_mechanism import ArtemisTestFixture, dataset, DataSet
import pytest
xfail = pytest.mark.xfail

@dataset([DataSet("test-01")])
class TestTest01(ArtemisTestFixture):
    """
    TODO: put there comments about the dataset
    """
    @xfail(reason="http://jira.canaltp.fr/browse/NAVITIAII-1126", raises=AssertionError)
    def test_test_01_01(self):
        self.journey(_from="stop_area:TS1:SA:2",
                     to="stop_area:TS1:SA:6", datetime="20041214T0700")

    def test_test_01_02(self):
        self.journey(_from="stop_area:TS1:SA:10",
                     to="stop_area:TS1:SA:12", datetime="20041214T0700")

