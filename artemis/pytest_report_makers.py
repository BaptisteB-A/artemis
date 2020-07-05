import ujson as json
import os
from artemis.configuration_manager import config
from deepdiff import DeepDiff
import urllib.parse


def request_diffs(ref_dict, resp_dict):
    requests = ["journeys", "places", "geo_status"]
    message = ""
    for req in requests:
        ref_req = ref_dict.get(req, [])
        resp_req = resp_dict.get(req, [])
        diff = DeepDiff(ref_req, resp_req)
        values_changed = diff.get("values_changed", [])
        updated_req_nb = set()
        for root in values_changed:
            req_id = root.split("]")[0]
            updated_req_nb.add(req_id)
        req_message = (
            "<u>" + req + " :</u>"
            "<ul><li>new " + req + " nb: {}\n</li>"
            "<li>discarded " + req + " nb: {}\n</li>"
            "<li>updated " + req + " nb: {}\n</li></ul>"
            "<details open><summary>CLICK ME</summary><p>\n\n"
            "<pre><code class='language-json\n'>"
            "{}\n"
            "</p></details>\n</code></pre>"
        ).format(
            len(diff.get("iterable_item_added", [])),
            len(diff.get("iterable_item_removed", [])),
            len(updated_req_nb),
            json.dumps(diff, indent=2),
        )
        message = "\n".join([message, req_message])
    return message


def add_to_report(test_name, test_query, report_message):
    failures_report_path = os.path.join(
        config["RESPONSE_FILE_PATH"], "failures_report.html"
    )

    reading_mode = "a" if os.path.exists(failures_report_path) else "w"
    with open(failures_report_path, reading_mode) as failures_report:
        failures_report.write("<p><strong>{}\n</strong></p>".format(test_name))
        encoded = urllib.parse.quote(test_query)
        failures_report.write(
            (
                "<p><a href=http://canaltp.github.io/navitia-playground/play.html?request={}\n>"
                "open query in navitia-playground</a></p>"
            ).format(encoded)
        )
        failures_report.write("{}\n".format(report_message))
