# SPDX-FileCopyrightText: 2023 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from maps_tools.convert import create_svg_selector


@pytest.mark.parametrize(
    "record,expected",
    [
        (
            {
                "new_cutlines": [
                    [218, 5746],
                    [5689, 5734],
                    [5686, 324],
                    [204, 318],
                    [218, 5746],
                ],
                "map": {
                    "image": {
                        "height": 6704,
                        "type": "iiif",
                        "url": "https://images.iiifhosting.com/iiif/3f3e57b48384ba9b6b25fb4657ac11b1112c1ac9a71d029b7b7791a9dc7146f9",
                        "width": 5934,
                    }
                },
            },
            '<svg width="5934" height="6704"><polygon points="218,5746 5689,5734 5686,324 204,318 218,5746" /></svg>',
        )
    ],
)
def test_gcp_length(record, expected):
    assert create_svg_selector(record) == expected

def test_empty_record():
    with pytest.raises(KeyError):
        create_svg_selector({})
