"""Lossless tagged JSON for the pandas scalar/axis types returned by Yahoo.

Unlike pandas JSON's limited decimal precision, float.hex preserves every bit.
Unsupported objects fail explicitly; no pickle or executable object decoding.
"""

from datetime import date, datetime
from decimal import Decimal

from .storage import encode


def pack(value):
    import numpy as np
    import pandas as pd

    if value is pd.NA:
        return ["NA"]
    if value is pd.NaT:
        return ["NaT"]
    if isinstance(value, pd.Timestamp):
        return ["timestamp", str(value.value), str(value.tz) if value.tz else None]
    if isinstance(value, np.generic):
        value = value.item()
    if value is None or isinstance(value, (str, bool, int)):
        return ["value", value]
    if isinstance(value, float):
        return ["float", value.hex()]
    if isinstance(value, Decimal):
        return ["decimal", str(value)]
    if isinstance(value, (date, datetime)):
        return ["datetime" if isinstance(value, datetime) else "date", value.isoformat()]
    if isinstance(value, tuple):
        return ["tuple", [pack(v) for v in value]]
    raise ValueError(f"unsupported frame scalar type: {type(value).__name__}")


def unpack(value):
    import pandas as pd

    kind, *args = value
    if kind == "NA":
        return pd.NA
    if kind == "NaT":
        return pd.NaT
    if kind == "value":
        return args[0]
    if kind == "float":
        return float.fromhex(args[0])
    if kind == "decimal":
        return Decimal(args[0])
    if kind == "timestamp":
        t = pd.Timestamp(int(args[0]), unit="ns", tz="UTC" if args[1] else None)
        return t.tz_convert(args[1]) if args[1] else t
    if kind in {"date", "datetime"}:
        return (date if kind == "date" else datetime).fromisoformat(args[0])
    if kind == "tuple":
        return tuple(unpack(v) for v in args[0])
    raise ValueError("unsupported tagged scalar")


def dtype_record(dtype):
    import pandas as pd

    if isinstance(dtype, pd.CategoricalDtype):
        return {"name": "category", "categories": axis_record(dtype.categories), "ordered": dtype.ordered}
    return {"name": str(dtype)}


def restore_dtype(record):
    import pandas as pd

    if record["name"] == "category":
        return pd.CategoricalDtype(restore_axis(record["categories"]), record["ordered"])
    return record["name"]


def axis_record(axis):
    import pandas as pd

    if isinstance(axis, pd.MultiIndex):
        return {"kind": "multi", "levels": [axis_record(v) for v in axis.levels],
                "codes": [v.tolist() for v in axis.codes], "names": [pack(v) for v in axis.names],
                "sortorder": axis.sortorder}
    if isinstance(axis, pd.RangeIndex):
        return {"kind": "range", "start": axis.start, "stop": axis.stop, "step": axis.step,
                "name": pack(axis.name)}
    return {"kind": "index", "dtype": dtype_record(axis.dtype), "name": pack(axis.name),
            "values": [pack(v) for v in axis], "freq": getattr(axis, "freqstr", None)}


def restore_axis(record):
    import pandas as pd

    if record["kind"] == "multi":
        return pd.MultiIndex(levels=[restore_axis(v) for v in record["levels"]], codes=record["codes"],
                             names=[unpack(v) for v in record["names"]], sortorder=record["sortorder"])
    if record["kind"] == "range":
        return pd.RangeIndex(record["start"], record["stop"], record["step"], name=unpack(record["name"]))
    result = pd.Index([unpack(v) for v in record["values"]], dtype=restore_dtype(record["dtype"]),
                      name=unpack(record["name"]), tupleize_cols=False)
    if isinstance(result, (pd.DatetimeIndex, pd.TimedeltaIndex)) and record["freq"]:
        result.freq = record["freq"]
    return result


def capture_frame(frame) -> bytes:
    import pandas as pd

    if not isinstance(frame, pd.DataFrame):
        raise ValueError("client return is not a DataFrame")
    record = {"schema_version": "client_frame_v1", "index": axis_record(frame.index),
              "columns": axis_record(frame.columns),
              "dtypes": [dtype_record(v) for v in frame.dtypes],
              "values": [[pack(v) for v in frame.iloc[:, i]] for i in range(len(frame.columns))]}
    return encode(record)


def restore_frame(content: bytes):
    import json
    import pandas as pd

    record = json.loads(content)
    if record["schema_version"] != "client_frame_v1":
        raise ValueError("unsupported client frame schema")
    index, columns = restore_axis(record["index"]), restore_axis(record["columns"])
    series = [pd.Series([unpack(v) for v in values], dtype=restore_dtype(dtype))
              for values, dtype in zip(record["values"], record["dtypes"], strict=True)]
    frame = pd.concat(series, axis=1) if series else pd.DataFrame(index=range(len(index)))
    frame.index, frame.columns = index, columns
    return frame
