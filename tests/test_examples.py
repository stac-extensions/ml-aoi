#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests all files in the `examples` directory against the JSON-schema.
"""
import glob
import os

import pystac
import pytest

from pystac_ml_aoi.extensions.ml_aoi import ML_AOI_SCHEMA_URI

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")


@pytest.mark.parametrize("file_path", glob.glob(f"{EXAMPLES_DIR}/**/collection_*.json", recursive=True))
def test_stac_collection_examples(
    file_path: str,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    col = pystac.Collection.from_file(file_path)
    valid_schemas = col.validate(validator=stac_validator)
    assert ML_AOI_SCHEMA_URI in valid_schemas


@pytest.mark.parametrize("file_path", glob.glob(f"{EXAMPLES_DIR}/**/item_*.geojson", recursive=True))
def test_stac_item_examples(
    file_path: str,
    stac_validator: pystac.validation.stac_validator.JsonSchemaSTACValidator,
) -> None:
    item = pystac.Item.from_file(file_path)
    valid_schemas = item.validate(validator=stac_validator)
    assert ML_AOI_SCHEMA_URI in valid_schemas
