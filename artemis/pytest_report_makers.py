import ujson as json
import os
from artemis.configuration_manager import config
from deepdiff import DeepDiff
import urllib.parse


def journeys_diff(ref_dict, resp_dict):
    ref_journeys = ref_dict.get("journeys", [])
    resp_journeys = resp_dict.get("journeys", [])
    diff = DeepDiff(ref_journeys, resp_journeys)
    message = (
        "<ul><li>new journeys nb: {}\n</li>"
        "<li>discarded journeys nb: {}\n</li>"
        "<li>updated journeys nb: {}\n</li></ul>"
        "<details open><summary>CLICK ME</summary><p>\n\n"
        "<pre><code class='language-json\n'>"
        "{}\n"
        "</p></details>\n</code></pre>"
    ).format(
        len(diff.get("dictionary_item_added", [])),
        len(diff.get("dictionary_item_removed", [])),
        len(diff.get("values_changed", [])),
        json.dumps(diff, indent=2),
    )
    return message


def places_diff(ref_dict, resp_dict):
    ref_places = ref_dict.get("places", [])
    resp_places = resp_dict.get("places", [])
    diff = DeepDiff(ref_places, resp_places)
    message = (
        "<ul><li>new places nb: {}\n</li>"
        "<li>discarded places nb: {}\n</li>"
        "<li>updated places nb: {}\n</li></ul>"
        "<details open><summary>CLICK ME</summary><p>\n\n"
        "<pre><code class='language-json\n'>"
        "{}\n"
        "</p></details>\n</code></pre>"
    ).format(
        len(diff.get("dictionary_item_added", [])),
        len(diff.get("iterable_item_removed", [])),
        len(diff.get("values_changed", [])),
        json.dumps(diff, indent=2),
    )
    return message


def geo_status_diff(ref_dict, resp_dict):
    ref_geo_status = ref_dict.get("geo_status", [])
    resp_geo_status = resp_dict.get("geo_status", [])
    diff = DeepDiff(ref_geo_status, resp_geo_status)
    print(ref_geo_status)
    print(resp_geo_status)

    message = (
        "<ul><li>new geo_status nb: {}\n</li>"
        "<li>discarded geo_status nb: {}\n</li>"
        "<li>updated geo_status nb: {}\n</li></ul>"
        "<details open><summary>CLICK ME</summary><p>\n\n"
        "<pre><code class='language-json\n'>"
        "{}\n"
        "</p></details>\n</code></pre>"
    ).format(
        len(diff.get("dictionary_item_added", [])),
        len(diff.get("dictionary_item_removed", [])),
        len(diff.get("values_changed", [])),
        json.dumps(diff, indent=2),
    )
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
