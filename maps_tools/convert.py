# SPDX-FileCopyrightText: 2022 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert Klokan annotations to IIIF annotations."""

import json
import click
import pathlib
import csv
import logging

@click.command()
@click.option('-o', '--output-dir', type=click.Path(dir_okay=True, path_type=pathlib.Path), required=True,
    show_default=True, default='./output', help='Directory to store converted files')
@click.option('-i', '--input-dir', type=click.Path(exists=True, dir_okay=True, path_type=pathlib.Path))
@click.option('-m', '--metadata', type=click.Path(exists=True, file_okay=True, path_type=pathlib.Path))
@click.option('-n', '--annos-per-page', type=int, default=100,
              help='Number of Annotations per AnnotationPage. Currently ignored.')
@click.option('-b', '--base-uri', type=str, required=True)
def cli(input_dir: pathlib.Path, output_dir: pathlib.Path, metadata: pathlib.Path, annos_per_page: int,
    base_uri: str):
    """Convert georeference data in given directories to IIIF annotations."""
    if not output_dir.exists():
        print('Creating', output_dir)
        output_dir.mkdir(parents=True)
    with metadata.open(mode='r', encoding='utf-8', newline='') as metadata_file:
        reader = csv.DictReader(metadata_file)
        for file_record in reader:
            georef_id = file_record['georef_klokan']
            input_file = f"{georef_id[0]}/{georef_id}.json"
            input_path = input_dir / pathlib.Path(input_file)
            print('Opening', input_path)
            image_uri = file_record['image_uri'][:-24]
            image_id = image_uri[42:]
            with input_path.open(encoding='utf-8', mode='r') as in_file:
                record = json.load(in_file)
            new_record = convert_to_iiif(record, input_file, image_uri, base_uri)
            output_filename = output_dir / georef_id[0] / input_path.name
            if not output_filename.parent.exists():
                output_filename.parent.mkdir(parents=True)
            with output_filename.open(mode='w') as out_file:
                json.dump(new_record, out_file, indent=2)
            print('Done!')


def convert_to_allmaps(record: dict, image_id: str, georef_id: str, image_uri: str) -> dict:
    """
    Convert a record to an Allmaps record.
    {
    "id": "26e384d4efabdb32",
    "gcps": [
      {
        "world": [
          97.1805877419104,
          3.2578402429992224
        ],
        "image": [
          578,
          3779
        ]
      },
      {
        "world": [
          95.75768658834603,
          2.8399231303739043
        ],
        "image": [
          349,
          3855
        ]
      },
      {
        "world": [
          98.6704303085887,
          3.5887634152449692
        ],
        "image": [
          834,
          3724
        ]
      },
      {
        "world": [
          96.13028951090241,
          4.147110928854772
        ],
        "image": [
          396,
          3629
        ]
      },
      {
        "world": [
          98.78380465867059,
          1.7403690250373955
        ],
        "image": [
          845,
          4039
        ]
      },
      {
        "world": [
          95.30603649176652,
          5.780419948549238
        ],
        "image": [
          252,
          3345
        ]
      },
      {
        "world": [
          97.48314719079927,
          5.244320402045915
        ],
        "image": [
          625,
          3441
        ]
      }
    ],
    "image": {
      "id": "d144156fc3c7f96c",
      "uri": "https://cdm21033.contentdm.oclc.org/digital/iiif/krt/1022",
      "type": "ImageService2",
      "width": 3493,
      "height": 4292
    },
    "version": 1,
    "pixelMask": [
      [
        196,
        3324
      ],
      [
        861,
        3323
      ],
      [
        856,
        4061
      ],
      [
        369,
        4057
      ],
      [
        370,
        3925
      ],
      [
        305,
        3852
      ],
      [
        191,
        3851
      ]
    ]
    }
    """
    result = {
        "id": georef_id,
        "image": {
            "id": image_id,
            "uri": image_uri,
            "type": "ImageService2",
            "width": record["map"]["image"]["width"],
            "height": record["map"]["image"]["height"]
        },
        "version": 1
    }
    gcps = []
    for control_point in record["new_gcps"]:
        gcp = {"world": control_point["location"],
               "image": control_point["pixel"] }
        gcps.append(gcp)
    # It looks like Allmaps doesn't need or want explicitly closed polygons
    pixel_mask = record["new_cutlines"][:-1]
    result["gcps"] = gcps
    result["pixelMask"] = pixel_mask
    return result

def convert_to_iiif(record: dict, georef_id: str, image_uri: str, base_uri: str) -> dict:
    """
    Convert a record to an annotation on a IIIF image.

    Args:
      record: enhanced Klokan record.
      georef_id: annotation identifier.
      image_uri: IIIF Image base URI.
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
                  "resourceCoords": control_point["pixel"]
                },
                "geometry": {
                  "type": "Point",
                  "coordinates": control_point["location"]
                }
              }
        gcps.append(gcp)
    return gcps

if __name__ == "__main__":
    cli()
