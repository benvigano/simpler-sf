import pytest
import json
import os

from simpler_sf._simpler_sf import _determine_object, SalesforceQueryParsingError


with open(os.path.join(os.path.dirname(__file__), "data", "determine_object_queries.json"), "r", encoding="utf-8") as f:
    soql_queries = json.load(f)


@pytest.mark.parametrize("case", soql_queries["valid"], ids=[c["query"] for c in soql_queries["valid"]])
def test_determine_object_valid(case):
    query = case["query"]
    expected = case["expected"]
    assert _determine_object(query) == expected


@pytest.mark.parametrize("case", soql_queries["edge_cases"], ids=[c["query"] for c in soql_queries["edge_cases"]])
def test_determine_object_edge_cases(case):
    query = case["query"]
    expected = case["expected"]
    assert _determine_object(query) == expected


@pytest.mark.parametrize("case", soql_queries["invalid"], ids=[str(c["query"]) for c in soql_queries["invalid"]])
def test_determine_object_invalid(case):
    query = case["query"]
    exception_substring = case["exception_substring"]

    if query is None:
        with pytest.raises(TypeError) as exc_info:
            _determine_object(query)
        assert exception_substring in str(exc_info.value)
    else:
        with pytest.raises(SalesforceQueryParsingError) as exc_info:
            _determine_object(query)
        assert exception_substring in str(exc_info.value)
