# SPDX-FileCopyrightText: 2022 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Check that manifests and images are available.
"""
import glob
import json
import requests
import time
import click
import csv
import logging


OUT_FIELDS = [
    'datetime',
    'manifest_url',
    'manifest_status',
    'manifest_time',
    'num_canvases',
    'canvas_uri',
    'canvas_status',
    'image_uri',
    'image_status',
    'image_time',
]
USER_AGENT = 'maps_tools/0.0.1; https://gitlab.services.universiteitleiden.nl/ub-leiden/maps-tools'

@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Produce more log messages')
@click.option('-f', '--overwrite', is_flag=True, help='Overwrite the output file')
@click.option('-o', '--out-file', required=True, type=click.Path(file_okay=True),
    help='Output file path')
@click.argument('file', required=True, type=click.Path(exists=True, file_okay=True))
def cli(file, out_file, overwrite, verbose):
    """Check that each manifest and image resolves"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    r_session = requests.sessions.Session()
    r_session.headers['User-Agent'] = USER_AGENT
    out_mode = 'a' if not overwrite else 'w'
    logging.info('Start checking manifests and images.')
    with open(file, 'r', encoding='utf-8', newline='') as in_file, open(out_file, out_mode, encoding='utf-8', newline='', buffering=1) as out_f:
        reader = csv.DictReader(in_file)
        # out_f.reconfigure(line_buffering=True, write_through=True)
        writer = csv.DictWriter(out_f, OUT_FIELDS, restval='')
        if out_f.tell() == 0:
            writer.writeheader()
        for line in reader:
            logging.debug(f'checking {line["manifest_url"]}...')
            out_row = {
                'datetime': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'manifest_url': line['manifest_url']
            }
            manifest = r_session.get(line["manifest_url"])
            out_row['manifest_status'] = manifest.status_code
            out_row['manifest_time'] = manifest.elapsed
            if manifest.status_code == 200:
                # hooray!
                logging.debug("succes!")
                manifest_data = manifest.json()
                out_row['num_canvases'] = len(manifest_data['sequences'][0]['canvases'])
                logging.debug('checking image')
                image = r_session.get(line["image_uri"])
                out_row['image_uri'] = line['image_uri']
                out_row['image_status'] = image.status_code
                out_row['image_time'] = image.elapsed
                # if image.status_code
            else:
                logging.debug("nope")
            writer.writerow(out_row)
            time.sleep(0.5)

if __name__ == "__main__":
    cli()
