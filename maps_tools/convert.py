# SPDX-FileCopyrightText: 2022 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Convert Klokan annotations to IIIF annotations.
"""

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
def cli(input_dir: pathlib.Path, output_dir: pathlib.Path, metadata: pathlib.Path):
    """
    Convert georeference data in given directories to IIIF annotations
    """
    if not output_dir.exists():
        print('Creating', output_dir)
        output_dir.mkdir(parents=True)
    with metadata.open(mode='r', encoding='utf-8', newline='') as metadata_file:
        reader = csv.DictReader(metadata_file)
        for file_record in reader:
            input_file = f"{file_record['georef_klokan'][0]}/{file_record['georef_klokan']}.json"
            input_path = input_dir / pathlib.Path(input_file)
            print('Opening', input_path)
            with input_path.open(encoding='utf-8', mode='r') as in_file:
                record = json.load(in_file)
            new_record = convert_to_allmaps(record)
            with (output_dir / input_path.name).open(mode='w') as out_file:
                json.dump(new_record, out_file, indent=2)
            print('Done!')


def convert_to_allmaps(record: dict) -> dict:
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
        "id": "FIXME",
        "image": {
            "id": "FIXME",
            "uri": "FIXME",
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



if __name__ == "__main__":
    cli()
