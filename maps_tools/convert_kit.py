# SPDX-FileCopyrightText: 2023 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert Klokan annotations to IIIF annotations."""

import json
import click
import pathlib
import csv
import logging
from iiif_prezi3 import AnnotationPage, Annotation
from .models import Point, PixelCoord, Gcp, FeatureList

@click.command()
@click.option('-o', '--output-dir', type=click.Path(dir_okay=True, path_type=pathlib.Path), required=True,
    show_default=True, default='./output', help='Directory to store converted files')
@click.option('-i', '--input-file', type=click.Path(exists=True, file_okay=True, path_type=pathlib.Path))
@click.option('-n', '--annos-per-page', type=int, default=100,
              help='Number of Annotations per AnnotationPage. Currently ignored.')
@click.option('-b', '--base-uri', type=str, required=True)
def cli(input_file: pathlib.Path, output_dir: pathlib.Path, annos_per_page: int,
    base_uri: str):
    """Convert georeference data in given directories to IIIF annotations."""
    if not output_dir.exists():
        print('Creating', output_dir)
        output_dir.mkdir(parents=True)
    with metadata.open(mode='r', encoding='utf-8', newline='') as metadata_file:
        reader = csv.DictReader(metadata_file)
        for file_record in reader:
            # Process each row
            print("doing something with this row")



def convert_to_iiif(record: dict, georef_id: str, image_uri: str, base_uri: str) -> dict:
    """
    Convert a record to an annotation on a IIIF image.

    Args:
      record: enhanced Klokan record.
      georef_id: annotation identifier.
      image_uri: IIIF Image base URI.
      base_uri: base URI for AnnotationPage and Annotation
    Returns:
      AnnotationPage containing a georeferencing Annotation.
    """
    result = {
      "@context": ["http://www.w3.org/ns/anno.jsonld"],
      "type": "AnnotationPage",
      "id": f"{base_uri}/{georef_id}",
      "items": [
        {
          "id": f"{base_uri}/{georef_id}#anno",
          "type": "Annotation",
          "@context": [
            "http://www.w3.org/ns/anno.jsonld",
            "http://geojson.org/geojson-ld/geojson-context.jsonld",
            "http://iiif.io/api/presentation/3/context.json"
          ],
          "motivation": "georeferencing",
          "target": {
            "type": "Image", # FIXME
            "source": image_uri + "/full/full/0/default.jpg",
            "service": [
              {
                "@id": image_uri,
                "type": "ImageService2"
              }
            ],
            "selector": {
              "type": "SvgSelector",
              "value": create_svg_selector(record)
            }
          },
          "body": {
            "type": "FeatureCollection",
            "purpose": "gcp-georeferencing",
            "transformation": {
              "type": "polynomial",
              "order": 0
            },
            "features": create_gcp_features(record)
          }
        }
      ]
    }

    return result


def create_svg_selector(record: dict) -> str:
    """Create an SVG selector with image dimensions and polygon."""
    points = " ".join([",".join(map(str, point)) for point in record["new_cutlines"]])
    height = record["map"]["image"]["height"]
    width = record["map"]["image"]["width"]
    return f'<svg width=\"{width}\" height=\"{height}\"><polygon points=\"{points}\" /></svg>'

def create_gcp_features(record: dict) -> list:
    """Create a list of Features for ground control points."""
    gcps = []
    for control_point in record["new_gcps"]:
        gcp = {
                "type": "Feature",
                "properties": {
                  "pixelCoords": control_point["pixel"]
                },
                "geometry": {
                  "type": "Point",
                  "coordinates": control_point["location"]
                }
              }
        gcps.append(gcp)
    return gcps

def naive_third_gcp(top_left: Gcp, bottom_right: Gcp) -> Gcp:
    """Naively generate a bottom-left ground control point from the top-left and bottom-right GCPs."""
    bottom_left = Gcp(
        coordinates=Point(lat=top_left.coordinates.lat, lng=bottom_right.coordinates.lng),
        resourceCoords=PixelCoord(x=top_left.resourceCoords.x, y=bottom_right.resourceCoords.y)
        )
    return bottom_left

def naive_fourth_gcp(top_left: Gcp, bottom_right: Gcp) -> Gcp:
    """Naively generate a top-right ground control point from the top-left and bottom-right GCPs."""
    top_right = Gcp(
        coordinates=Point(lat=bottom_right.coordinates.lat, lng=top_left.coordinates.lng),
        resourceCoords=PixelCoord(x=bottom_right.resourceCoords.x, y=top_left.resourceCoords.y)
        )
    return top_right

if __name__ == "__main__":
    cli()
