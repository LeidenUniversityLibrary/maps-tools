# SPDX-FileCopyrightText: 2023 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import json
from maps_tools.convert_kit import naive_third_gcp, naive_fourth_gcp
from maps_tools.models import Gcp, Point, PixelCoord, FeatureList

@pytest.fixture
def existing_gcps():
    return [
        Gcp(
            coordinates=Point(lat=-6.87388888888889, lng=107.565833333333),
            resourceCoords=PixelCoord(x=633, y=613)
            ),
        Gcp(
            coordinates=Point(lat=-6.94833333333333, lng=107.65),
            resourceCoords=PixelCoord(x=6257, y=5360)
            )
        ]

@pytest.fixture
def bottom_left_gcp():
    return Gcp(
            coordinates=Point(lat=-6.87388888888889, lng=107.65),
            resourceCoords=PixelCoord(x=633, y=5360)
            )

@pytest.fixture
def top_right_gcp():
    return Gcp(
            coordinates=Point(lat=-6.94833333333333, lng=107.565833333333),
            resourceCoords=PixelCoord(x=6257, y=613)
            )

def test_third_gcp(existing_gcps, bottom_left_gcp):
    """Check that the naive generation of a third GCP works."""
    assert naive_third_gcp(existing_gcps[0], existing_gcps[1]) == bottom_left_gcp


def test_fourth_gcp(existing_gcps, top_right_gcp):
    """Check that the naive generation of a third GCP works."""
    assert naive_fourth_gcp(existing_gcps[0], existing_gcps[1]) == top_right_gcp


def test_gcp_dict(bottom_left_gcp):
    """Check that a GCP is serialised as a dict correctly."""
    gcp_dict = bottom_left_gcp.dict(by_alias=True)
    assert "type" in gcp_dict.keys()
    assert "coordinates" in gcp_dict.keys()
    assert "resourceCoords" in gcp_dict.keys()

# def test_gcp_json(bottom_left_gcp):
#     """Check that a GCP serialised to JSON has expected structure."""
#     gcp_json = bottom_left_gcp.json(models_as_dict=False)
#     print(gcp_json)
#     gcp_json_dict = json.loads(gcp_json)
#     assert "type" in gcp_json_dict.keys()
#     assert "geometry" in gcp_json_dict.keys()
#     assert "properties" in gcp_json_dict.keys()

def test_gcp_list_json(existing_gcps):
    feature_list = FeatureList(features=existing_gcps)
    fl_json = feature_list.json(models_as_dict=False)
    print(fl_json)
    fl_dict = json.loads(fl_json)
    assert "geometry" in fl_dict["features"][0].keys()
