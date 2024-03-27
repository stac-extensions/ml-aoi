from typing import cast

import json
import pytest
import pystac
from dateutil.parser import parse as dt_parse

from pystac_ml_aoi.extensions.ml_aoi import ML_AOI_SCHEMA_PATH, ML_AOI_SCHEMA_URI


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
