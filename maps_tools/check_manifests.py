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

@click.command()
def cli():
    """Check that each manifest and image resolves"""
    print("Hello")

if __name__ == "__main__":
    cli()
