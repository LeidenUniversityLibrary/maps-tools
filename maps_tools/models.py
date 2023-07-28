# SPDX-FileCopyrightText: 2023 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Model classes for georeferencing annotations"""

from pydantic import BaseModel, NonNegativeInt, Field
import json
from typing import List

class Point(BaseModel):
    lat: float
    lng: float

class PixelCoord(BaseModel):
    x: NonNegativeInt
    y: NonNegativeInt

def wrap_geometry(p: Point):
    geom = {'type': 'Point', 'coordinates': [p.lat, p.lng]}
    return f'"geometry": {json.dumps(geom)}'

def wrap_properties(p: PixelCoord):
    geom = {"resourceCoords": [p.x, p.y]}
    return f'"properties": {json.dumps(geom)}'

class Gcp(BaseModel):
    type: str = Field('Feature', const=True)
    coordinates: Point
    resourceCoords: PixelCoord

def gcp_as_feature(gcp: Gcp):
    result = gcp.dict(include={'type': True})
    result["properties"] = {
        "resourceCoords": [gcp.resourceCoords.x, gcp.resourceCoords.y]
    }
    result["geometry"] = {
        "type": "Point",
        "coordinates": [gcp.coordinates.lat, gcp.coordinates.lng]
    }
    return result


class FeatureList(BaseModel):
    features: List[Gcp]

    class Config:
        json_encoders = {
            Gcp: gcp_as_feature
        }
