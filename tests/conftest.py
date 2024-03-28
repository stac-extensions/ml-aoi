import json
from typing import cast

import pystac
import pytest

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
