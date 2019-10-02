from artemis.configuration_manager import config

if config.get("USE_ARTEMIS_NG"):
    from artemis.base_pytest import ArtemisTestFixture
else:
    from artemis.test_mechanism import ArtemisTestFixture
