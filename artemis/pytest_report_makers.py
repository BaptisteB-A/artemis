import ujson as json
import jsondiff

def journeys_diff(ref, output):
    with open(ref) as ref_f, open(output) as output_f:
        ref_j = json.load(ref_f)
        out_j = json.load(output_f)
        diff = jsondiff.diff(ref_j['response'].get('journeys', []), out_j['response'].get('journeys', []),
                             syntax='symmetric')

        updated_nb = sum(str(k).isdigit() for k in diff.keys())

        message = (
            "* new journeys nb: {}\n"
            "* discarded journeys nb: {}\n"
            "* updated journeys nb: {}\n"
            "\n<details open><summary>CLICK ME</summary><p>\n"
            "\n```json\n{}\n```\n"
            "\n</p></details>\n"
        ).format(len(diff.get(jsondiff.symbols.insert, [])),
                 len(diff.get(jsondiff.symbols.delete, [])),
                 updated_nb,
                 json.dumps(diff, indent=2))
        return message


def ptref_diff(ref, output):
    return "* ptref diff not yet implemented"

def example_diff(ref, output):
    return "* example diff not yet implemented"
