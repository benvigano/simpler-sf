from simpler_sf._simpler_sf import _determine_object
from samples import test_queries


def test__determine_object() -> None:
    for query, sf_object in test_queries.items():

        inline_query = " ".join(line.strip() for line in query.splitlines())

        assert _determine_object(inline_query).lower() == sf_object.lower()