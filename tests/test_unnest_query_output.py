import pytest
import json
import os

from simpler_sf._simpler_sf import _unnest_query_output


with open(os.path.join(os.path.dirname(__file__), "data", "unnest_query_outputs.json"), "r", encoding="utf-8") as f:
    raw_outputs = json.load(f)


@pytest.mark.parametrize("case", raw_outputs["valid"], ids=[c["id"] for c in raw_outputs["valid"]])
def test_unnest_query_output(case):
    raw_output = case["raw_output"]
    unnested_output = case["unnested_output"]
    assert _unnest_query_output(raw_output) == unnested_output
