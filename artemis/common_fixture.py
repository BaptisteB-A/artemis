import logging
import inspect
import psycopg2
import requests

import artemis.utils as utils

from artemis.configuration_manager import config

logger = logging.getLogger(__name__)


# given a cursor on a db, and table names separated by a comma (ex: "tata, toto, titi")
def truncate_tables(cursor, table_names_string):
    logger.debug("query db: TRUNCATE {} CASCADE ;".format(table_names_string))
    cursor.execute("TRUNCATE {} CASCADE ;".format(table_names_string))


# the time cost is around 1.3s on artemis platform
def clean_kirin_db():
    logger.info("cleaning kirin database")
    conn = psycopg2.connect(config["KIRIN_DB"])
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT relname FROM pg_stat_user_tables WHERE relname != 'alembic_version';"
        )
        tables = cur.fetchall()

        truncate_tables(
            cur, ", ".join(e[0] for e in tables if e[0] not in ("layer", "topology"))
        )

        conn.commit()

        cur.execute(
            "INSERT INTO contributor SELECT 'realtime.sherbrooke','ca-qc-sherbrooke','token_to_be_modified',"
            "'feed_url_to_be_modified','gtfs-rt'"
        )
        cur.execute(
            "INSERT INTO contributor SELECT 'realtime.cots','sncf','token_to_be_modified',"
            "'feed_url_to_be_modified','cots'"
        )
        conn.commit()
        logger.debug("kirin db purge done")
    except Exception:
        logger.exception("problem with kirin db")
        conn.close()
        assert False, "problem while cleaning kirin db"
    conn.close()


class CommonTestFixture(object):
    def get_file_name(self):
        """
        create the name of the file for storing the query.

        the file is:

        {fixture_name}/{function_name}_{md5_on_url}(|_{call_number}).json

        if a custom_name is provided we take it, else we create a md5 on the url.
        a custom_name must be provided is the same call is done twice in the same test function
        """
        mro = inspect.getmro(self.__class__)
        class_name = "Test{}".format(mro[1].__name__)
        scenario = mro[0].data_sets[0].scenario

        func_name = utils.get_calling_test_function()
        test_name = "{}/{}/{}".format(class_name, scenario, func_name)

        self.test_counter[test_name] += 1

        if self.test_counter[test_name] > 1:
            return "{}_{}.json".format(test_name, self.test_counter[test_name] - 1)
        else:
            return "{}.json".format(test_name)

    @staticmethod
    def _send_cots(cots_file_name):
        r = requests.post(
            config["KIRIN_API"] + "/cots",
            data=utils.get_rt_data(cots_file_name).encode("UTF-8"),
            headers={"Content-Type": "application/json;charset=utf-8"},
        )
        r.raise_for_status()

    def send_and_wait(self, rt_file_name):
        """
        Send a COTS and wait until the data is reloaded
        :param rt_file_name: name of the real-time feed file (obviously)
        """
        if self.check_ref:
            return

        if len(self.data_sets) > 1:
            logger.warning(" >1 data_set for test class !!!")
        coverage = self.data_sets[0].name
        last_rt_data_loaded = self.get_last_rt_loaded_time(coverage)
        self._send_cots(rt_file_name)
        self.wait_for_rt_reload(last_rt_data_loaded, coverage)
