#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test functionalities provided by :class:`MLAOI_Extension`.
"""
import unittest
import pystac
import shapely
from dateutil.parser import parse as dt_parse

from pystac.extensions.label import LabelExtension
from pystac_ml_aoi.extensions.ml_aoi import ML_AOI_Extension, ML_AOI_SCHEMA_URI


def test_ml_aoi_pystac_collection():
    """
    Validate extending a STAC Collection with ML-AOI extension.

    Example reference STAC Collection taken from:
    - https://github.com/stac-extensions/ml-aoi/blob/main/examples/collection_EuroSAT-subset-train.json
    - https://github.com/ai-extensions/stac-data-loader/blob/main/data/EuroSAT/stac/subset/train/collection.json
    """
    ext = pystac.Extent(
        spatial=pystac.SpatialExtent(
            bboxes=[[-7.882190080512502, 37.13739173208318, 27.911651652899923, 58.21798141355221]],
        ),
        temporal=pystac.TemporalExtent(
            intervals=[dt_parse("2015-06-27T10:25:31.456Z"), dt_parse("2017-06-14T00:00:00Z")],
        ),
    )
    col = pystac.Collection(
        id="EuroSAT-subset-train",
        description=(
            "EuroSAT dataset with labeled annotations for land-cover classification and associated imagery. "
            "This collection represents samples part of the train split set for training machine learning algorithms."
        ),
        extent=ext,
        license="MIT",
        catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED,
    )
    ml_aoi_col = ML_AOI_Extension.ext(col, add_if_missing=True)
    ml_aoi_col.apply(split="train")
    assert ML_AOI_SCHEMA_URI in col.stac_extensions


def test_ml_aoi_pystac_item():
    """
    Validate extending a STAC Collection with ML-AOI extension.

    Example reference STAC Item taken from:
    - https://github.com/stac-extensions/ml-aoi/blob/main/examples/item_EuroSAT-subset-train-sample-42-class-Residential.geojson
    - https://github.com/ai-extensions/stac-data-loader/blob/main/data/EuroSAT/stac/subset/train/item-42.json
    """
    geom = {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -3.1380012709408427,
              51.531997746547134
            ],
            [
              -3.1380012709408427,
              51.53774085855159
            ],
            [
              -3.1472537450112785,
              51.53774085855159
            ],
            [
              -3.1472537450112785,
              51.531997746547134
            ],
            [
              -3.1380012709408427,
              51.531997746547134
            ]
          ]
        ]
      }
    bbox = list(shapely.geometry.shape(geom).bounds)
    item = pystac.Item(
        id="EuroSAT-subset-train-sample-42-class-Residential",
        geometry=geom,
        bbox=bbox,
        start_datetime=dt_parse("2015-06-27T10:25:31.456Z"),
        end_datetime=dt_parse("2017-06-14T00:00:00Z"),
        datetime=None,
        properties={}
    )
    item = LabelExtension.ext(item, add_if_missing=True)
    item = ML_AOI_Extension.ext(item, add_if_missing=True)
    #item = cast(item, Union[pystac.Item, LabelExtension, MLAOI_Extension])
    item.apply(properties)



if __name__ == '__main__':
    unittest.main()
