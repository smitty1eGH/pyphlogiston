from collections import OrderedDict

# from botofier import toD, toJ

# Utilities supporting unit tests pertaining to botocore test cases


def toD(od):
    """Transform a botocore OrderedDict as a regular dict."""

    def _mems(od):
        return od

    out = {}
    try:
        for k, v in od.items():
            if isinstance(v, OrderedDict):
                out[k] = toD(v)
            elif isinstance(v, list):
                tmp = {}
                for l in v:
                    m = toD(l)
                    for n, o in m.items():
                        if n in tmp:
                            tmp[n].append(o)
                        else:
                            tmp[n] = [o]
                out[k] = tmp
            else:
                out[k] = v
    except AttributeError as e:
        x = {"type": "str", "mems": None}
        x["mems"] = _mems(od)
        return x
    else:
        return out


def toJ(od):
    return json.loads(json.dumps(toD(od)))
