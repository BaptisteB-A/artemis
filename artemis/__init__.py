import logging
import os
import shutil
from artemis.configuration_manager import config

# NOTE: I did not manage to use the setup_module for a global init,
# so this is done here (but it'll be more difficult if we need a global teardown...as

logging.getLogger().warning("setup before all")
# clean up the response dir
logging.getLogger().info("removing output dir {}".format(config["RESPONSE_FILE_PATH"]))
if os.path.exists(config["RESPONSE_FILE_PATH"]):
    shutil.rmtree(config["RESPONSE_FILE_PATH"])
