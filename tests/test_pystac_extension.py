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

from pystac.extensions.label import LabelExtension, LabelTask, LabelType
from pystac_ml_aoi.extensions.ml_aoi import (
    ML_AOI_Extension,
    ML_AOI_CollectionExtension,
    ML_AOI_ItemExtension,
    ML_AOI_SCHEMA_PATH,
    ML_AOI_SCHEMA_URI,
    ML_AOI_Role,
    ML_AOI_Split,
)


EUROSAT_EXAMPLE_BASE_URL = "https://raw.githubusercontent.com/ai-extensions/stac-data-loader/0.5.0/data/EuroSAT"
EUROSAT_EXAMPLE_ASSET_ITEM_URL = (
    EUROSAT_EXAMPLE_BASE_URL +
    "/stac/subset/train/item-42.json"
)
EUROSAT_EXAMPLE_ASSET_LABEL_URL = (
    EUROSAT_EXAMPLE_BASE_URL +
    "/data/subset/ds/images/remote_sensing/otherDatasets/sentinel_2/label/Residential/Residential_1331.geojson"
)
EUROSAT_EXAMPLE_ASSET_RASTER_URL = (
    EUROSAT_EXAMPLE_BASE_URL +
    "/data/subset/ds/images/remote_sensing/otherDatasets/sentinel_2/tif/Residential/Residential_1331.tif"
)


@pytest.fixture(scope="session", name="stac_validator", autouse=True)
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
    validation_schema = json.loads(pystac.StacIO.default().read_text(ML_AOI_SCHEMA_PATH))
    validator.schema_cache[ML_AOI_SCHEMA_URI] = validation_schema
    pystac.validation.RegisteredValidator.set_validator(validator)  # apply globally to allow 'STACObject.validate()'
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


@pytest.fixture(scope="function", name="item")
def make_base_stac_item() -> pystac.Item:
    """
    Example reference STAC Item taken from:
    - https://github.com/stac-extensions/ml-aoi/blob/main/examples/item_EuroSAT-subset-train-sample-42-class-Residential.geojson
    - https://github.com/ai-extensions/stac-data-loader/blob/main/data/EuroSAT/stac/subset/train/item-42.json

    The ML-AOI fields are to be extended by the various unit test functions.
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
    asset_label = pystac.Asset(
        href=EUROSAT_EXAMPLE_ASSET_LABEL_URL,
        media_type=pystac.MediaType.GEOJSON,
        roles=["data"],
        extra_fields={
            "ml-aoi:role": ML_AOI_Role.LABEL,
        }
    )
    asset_raster = pystac.Asset(
        href=EUROSAT_EXAMPLE_ASSET_RASTER_URL,
        media_type=pystac.MediaType.GEOTIFF,
        roles=["data"],
        extra_fields={
            "ml-aoi:reference-grid": True,
            "ml-aoi:role": ML_AOI_Role.FEATURE,
        }
    )
    item = pystac.Item(
        id="EuroSAT-subset-train-sample-42-class-Residential",
        geometry=geom,
        bbox=bbox,
        start_datetime=dt_parse("2015-06-27T10:25:31.456Z"),
        end_datetime=dt_parse("2017-06-14T00:00:00Z"),
        datetime=None,
        properties={},
        assets={"label": asset_label, "raster": asset_raster},
    )
    label_item = LabelExtension.ext(item, add_if_missing=True)
    label_item.apply(
        label_description="ml-aoi-test",
        label_type=LabelType.VECTOR,
        label_tasks=[LabelTask.CLASSIFICATION, LabelTask.SEGMENTATION],
        label_properties=["class"],
    )
    return item


def test_ml_aoi_pystac_collection_with_apply_method(
    collection: pystac.Collection,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    assert ML_AOI_SCHEMA_URI not in collection.stac_extensions
    ml_aoi_col = ML_AOI_Extension.ext(collection, add_if_missing=True)
    ml_aoi_col.apply(split=[ML_AOI_Split.TRAIN])
    assert ML_AOI_SCHEMA_URI in collection.stac_extensions
    collection.validate()
    ml_aoi_col_json = collection.to_dict()
    assert ml_aoi_col_json["summaries"] == [{"ml-aoi:split": "train"}]


def test_ml_aoi_pystac_collection_with_field_property(
    collection: pystac.Collection,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    assert ML_AOI_SCHEMA_URI not in collection.stac_extensions
    ml_aoi_col = ML_AOI_Extension.ext(collection, add_if_missing=True)
    ml_aoi_col.split = [ML_AOI_Split.TRAIN]
    assert ML_AOI_SCHEMA_URI in collection.stac_extensions
    collection.validate()
    ml_aoi_col_json = collection.to_dict()
    assert ml_aoi_col_json["summaries"] == [{"ml-aoi:split": "train"}]


def test_ml_aoi_pystac_item_with_apply_method(
    item: pystac.Item,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    assert ML_AOI_SCHEMA_URI not in item.stac_extensions
    ml_aoi_item = ML_AOI_Extension.ext(item, add_if_missing=True)
    ml_aoi_item.apply(split=ML_AOI_Split.TRAIN)
    assert ML_AOI_SCHEMA_URI in item.stac_extensions
    item.validate()
    ml_aoi_item_json = item.to_dict()
    assert ml_aoi_item_json["properties"]["ml-aoi:split"] == "train"


def test_ml_aoi_pystac_item_with_field_property(
    item: pystac.Item,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    assert ML_AOI_SCHEMA_URI not in item.stac_extensions
    ml_aoi_item = ML_AOI_Extension.ext(item, add_if_missing=True)
    ml_aoi_item.split = ML_AOI_Split.TRAIN
    assert ML_AOI_SCHEMA_URI in item.stac_extensions
    item.validate()
    ml_aoi_item_json = item.to_dict()
    assert ml_aoi_item_json["properties"]["ml-aoi:split"] == "train"


def test_ml_aoi_pystac_item_filter_assets(
    item: pystac.Item,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    """
    Validate extending a STAC Collection with ML-AOI extension.
    """
    assert ML_AOI_SCHEMA_URI not in item.stac_extensions
    ml_aoi_item = cast(ML_AOI_ItemExtension, ML_AOI_Extension.ext(item, add_if_missing=True))
    ml_aoi_item.split = ML_AOI_Split.TRAIN
    assets = ml_aoi_item.get_assets(reference_grid=True)
    assert len(assets) == 1 and "raster" in assets


if __name__ == "__main__":
    unittest.main()
