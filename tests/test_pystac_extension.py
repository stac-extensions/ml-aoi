#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test functionalities provided by :class:`MLAOI_Extension`.
"""
import json
import unittest
import pystac
import pytest
import requests
import shapely
from dateutil.parser import parse as dt_parse
from typing import cast

from pystac.extensions.label import LabelExtension
from pystac_ml_aoi.extensions.ml_aoi import ML_AOI_Extension, ML_AOI_SCHEMA_PATH, ML_AOI_SCHEMA_URI


@pytest.fixture(scope="session", name="validator", autouse=True)
def make_stac_ml_aoi_validator(
    request: pytest.FixtureRequest,
) -> pystac.validation.stac_validator.JsonSchemaSTACValidator:
    """
    Update the :class:`pystac.validation.RegisteredValidator` with the local ML-AOI JSON schema definition.

    Because the schema is *not yet* uploaded to the expected STAC schema URI,
    any call to :func:`pystac.validation.validate` or :meth:`pystac.stac_object.STACObject.validate` results
    in ``GetSchemaError`` when the schema retrieval is attempted by the validator. By adding the schema to the
    mapping beforehand, remote resolution can be bypassed temporarily.
    """
    validator = pystac.validation.RegisteredValidator.get_validator()
    validator = cast(pystac.validation.stac_validator.JsonSchemaSTACValidator, validator)
    validator.registry.with_contents([
        (
            ML_AOI_SCHEMA_URI,
            json.loads(pystac.StacIO.default().read_text(ML_AOI_SCHEMA_PATH)),
        )
    ])
    return validator


@pytest.fixture(scope="function", name="collection")
def make_base_stac_collection() -> pystac.Collection:
    """
    Example reference STAC Collection taken from:
    - https://github.com/stac-extensions/ml-aoi/blob/main/examples/collection_EuroSAT-subset-train.json
    - https://github.com/ai-extensions/stac-data-loader/blob/main/data/EuroSAT/stac/subset/train/collection.json

    The ML-AOI fields are to be extended by the various unit test functions.
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
    return col


def test_ml_aoi_pystac_collection_with_apply_method(collection: pystac.Collection):
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    ml_aoi_col = ML_AOI_Extension.ext(collection, add_if_missing=True)
    ml_aoi_col.apply(split=["train"])
    assert ML_AOI_SCHEMA_URI in collection.stac_extensions
    collection.validate()
    ml_aoi_col_json = collection.to_dict()
    assert ml_aoi_col_json["summaries"] == [{"ml-aoi:splits": "train"}]


def test_ml_aoi_pystac_collection_with_field_property(collection: pystac.Collection):
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    ml_aoi_col = ML_AOI_Extension.ext(collection, add_if_missing=True)
    ml_aoi_col.split = ["train"]
    assert ML_AOI_SCHEMA_URI in collection.stac_extensions
    collection.validate()
    ml_aoi_col_json = collection.to_dict()
    assert ml_aoi_col_json["summaries"] == [{"ml-aoi:splits": "train"}]


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
