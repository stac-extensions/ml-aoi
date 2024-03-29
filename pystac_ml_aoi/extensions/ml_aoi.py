#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities to extend :mod:`pystac` objects with STAC ML-AOI extension.
"""
import abc
import json
import os
from typing import Any, Generic, Iterable, List, Literal, Optional, Protocol, TypeVar, Union, cast, get_args

import pystac
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.fields import FieldInfo
from pystac.extensions import item_assets
from pystac.extensions.base import (  # generic pystac.STACObject
    ExtensionManagementMixin,
    PropertiesExtension,
    S,
    SummariesExtension
)
from pystac.extensions.hooks import ExtensionHooks
from pystac.utils import StringEnum

T = TypeVar("T", pystac.Collection, pystac.Item, pystac.Asset, item_assets.AssetDefinition)
SchemaName = Literal["ml-aoi"]

AnySummary = Union[list[Any], pystac.RangeSummary[Any], dict[str, Any], None]

_PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "../../.."))
ML_AOI_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "json-schema/schema.json")

with open(ML_AOI_SCHEMA_PATH, mode="r", encoding="utf-8") as schema_file:
    ML_AOI_SCHEMA = json.load(schema_file)

ML_AOI_SCHEMA_ID: SchemaName = get_args(SchemaName)[0]
ML_AOI_SCHEMA_URI: str = ML_AOI_SCHEMA["$id"].split("#")[0]
ML_AOI_PREFIX = f"{ML_AOI_SCHEMA_ID}:"
ML_AOI_PROPERTY = f"{ML_AOI_SCHEMA_ID}_".replace("-", "_")


class ExtendedEnum(StringEnum):
    @classmethod
    def values(cls) -> List[str]:
        return list(cls.__members__.values())


class ML_AOI_Split(ExtendedEnum):
    TRAIN: Literal["train"] = "train"
    VALIDATE: Literal["validate"] = "validate"
    TEST: Literal["test"] = "test"


ML_AOI_SplitType = Union[
    ML_AOI_Split,
    Literal[
        ML_AOI_Split.TRAIN,
        ML_AOI_Split.VALIDATE,
        ML_AOI_Split.TEST,
    ]
]


class ML_AOI_Role(ExtendedEnum):
    LABEL: Literal["label"] = "label"
    FEATURE: Literal["feature"] = "feature"


ML_AOI_RoleType = Union[
    ML_AOI_Role,
    Literal[
        ML_AOI_Role.LABEL,
        ML_AOI_Role.FEATURE,
    ]
]


class ML_AOI_Resampling(ExtendedEnum):
    NEAR: Literal["near"] = "near"
    BILINEAR: Literal["bilinear"] = "bilinear"
    CUBIC: Literal["cubic"] = "cubic"
    CUBCSPLINE: Literal["cubcspline"] = "cubcspline"
    LANCZOS: Literal["lanczos"] = "lanczos"
    AVERAGE: Literal["average"] = "average"
    RMS: Literal["rms"] = "rms"
    MODE: Literal["mode"] = "mode"
    MAX: Literal["max"] = "max"
    MIN: Literal["min"] = "min"
    MED: Literal["med"] = "med"
    Q1: Literal["q1"] = "q1"
    Q3: Literal["q3"] = "q3"
    SUM: Literal["sum"] = "sum"


ML_AOI_ResamplingType = Union[
    Literal[
        ML_AOI_Resampling.NEAR,
        ML_AOI_Resampling.BILINEAR,
        ML_AOI_Resampling.CUBIC,
        ML_AOI_Resampling.CUBCSPLINE,
        ML_AOI_Resampling.LANCZOS,
        ML_AOI_Resampling.AVERAGE,
        ML_AOI_Resampling.RMS,
        ML_AOI_Resampling.MODE,
        ML_AOI_Resampling.MAX,
        ML_AOI_Resampling.MIN,
        ML_AOI_Resampling.MED,
        ML_AOI_Resampling.Q1,
        ML_AOI_Resampling.Q3,
        ML_AOI_Resampling.SUM,
    ]
]

# pystac references
SCHEMA_URI = ML_AOI_SCHEMA_URI
SCHEMA_URIS = [SCHEMA_URI]
PREFIX = ML_AOI_PREFIX


def add_ml_aoi_prefix(name: str) -> str:
    return ML_AOI_PREFIX + name if "datetime" not in name else name


class ML_AOI_BaseFields(BaseModel, validate_assignment=True):
    """
    ML-AOI base definition to validate fields and properties.
    """

    model_config = ConfigDict(alias_generator=add_ml_aoi_prefix, populate_by_name=True, extra="ignore")

    @model_validator(mode="after")
    def validate_one_of(self) -> "ML_AOI_BaseFields":
        """
        All fields are optional, but at least one is required.

        Additional ``ml-aoi:`` prefixed properties are allowed as well, but no additional validation is performed.
        """
        # note:
        #   purposely omit 'by_alias=True' to have any fields defined, with/without extension prefix
        #   if the extension happened to use any non-prefixed field, they would be validated as well
        fields = self.model_dump()
        # fields = {
        #     f: v for f, v in fields.items()
        #     if f.startswith(ML_AOI_PREFIX) and f.replace(ML_AOI_PREFIX, "")
        # }
        if len(fields) < 1 or all(value is None for value in fields.values()):
            raise ValueError("ML-AOI extension must provide at least one valid field.")
        return self


class ML_AOI_ItemProperties(ML_AOI_BaseFields, validate_assignment=True):
    """
    ML-AOI properties for STAC Items.
    """

    split: Optional[ML_AOI_Split]  # split is required since it is the only available field


class ML_AOI_CollectionFields(ML_AOI_BaseFields, validate_assignment=True):
    """
    ML-AOI properties for STAC Collections.
    """

    split: Optional[List[ML_AOI_Split]]  # split is required since it is the only available field


class ML_AOI_AssetFields(ML_AOI_BaseFields, validate_assignment=True):
    role: Optional[ML_AOI_Role] = None
    reference_grid: Optional[bool] = Field(alias="reference-grid", default=None)
    resampling_method: Optional[ML_AOI_Resampling] = Field(
        alias="resampling-method",
        description="Supported GDAL resampling method (https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-r)",
        default=None,
    )


class ML_AOI_LinkFields(ML_AOI_BaseFields, validate_assignment=True):
    role: Optional[ML_AOI_Role]  # role is required since it is the only available field


# class ML_AOI_MetaClass(type, abc.ABC):
#     @property
#     @abc.abstractmethod
#     def model(self) -> ML_AOI_BaseFields:
#         raise NotImplementedError

class ML_AOI_MetaClass(Protocol):
    model: ML_AOI_BaseFields


class ML_AOI_Extension(
    ML_AOI_MetaClass,
    Generic[T],
    ExtensionManagementMixin[Union[pystac.Asset, pystac.Item, pystac.Collection]],
    abc.ABC,
):
    @abc.abstractmethod
    def get_ml_aoi_property(self, prop_name: str, *, _ml_aoi_required: bool) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def set_ml_aoi_property(
        self,
        prop_name: str,
        value: Any,
        pop_if_none: bool = True,
        *,
        _ml_aoi_required: bool,
    ) -> None:
        raise NotImplementedError

    def __getitem__(self, prop_name):
        return self.get_ml_aoi_property(prop_name, _ml_aoi_required=False)

    def __setattr__(self, prop_name, value):
        self.set_ml_aoi_property(prop_name, value, _ml_aoi_required=False, pop_if_none=True)

    @classmethod
    def _is_ml_aoi_property(cls, prop_name: str):
        return (
            prop_name.startswith(ML_AOI_PREFIX)
            or prop_name.startswith(ML_AOI_PROPERTY)
            or prop_name in cls.model.model_fields
        )

    @classmethod
    def _retrieve_ml_aoi_property(cls, prop_name: str, *, _ml_aoi_required: bool) -> Optional[FieldInfo]:
        if not _ml_aoi_required and not cls._is_ml_aoi_property(prop_name):
            return
        try:
            return cls.model.model_fields[prop_name]
        except KeyError:
            raise AttributeError(f"Name '{prop_name}' is not a valid ML-AOI field.")

    @classmethod
    def _validate_ml_aoi_property(cls, prop_name: str, value: Any) -> None:
        model = cls.model.model_construct()
        validator = cls.model.__pydantic_validator__
        validator.validate_assignment(model, prop_name, value)

    @property
    def name(self) -> SchemaName:
        return ML_AOI_SCHEMA_ID

    def apply(
        self,
        fields: Union[
            ML_AOI_CollectionFields,
            ML_AOI_ItemProperties,
            ML_AOI_AssetFields,
            ML_AOI_LinkFields,
            dict[str, Any]
        ] = None,
        **extra_fields: Any,
    ) -> None:
        """
        Applies ML-AOI Extension properties to the extended :class:`~pystac.Item` or :class:`~pystac.Asset`.
        """
        if not fields:
            fields = {}
        fields.update(extra_fields)
        obj = (
            getattr(self, "collection", None) or
            getattr(self, "item", None) or
            getattr(self, "asset", None) or
            getattr(self, "link")
        )
        if isinstance(fields, dict):
            if isinstance(obj, pystac.Collection):
                fields = ML_AOI_CollectionFields(**fields)
            elif isinstance(obj, pystac.Item):
                fields = ML_AOI_ItemProperties(**fields)
            elif isinstance(obj, pystac.Asset):
                fields = ML_AOI_AssetFields(**fields)
            elif isinstance(obj, pystac.Link):
                fields = ML_AOI_LinkFields(**fields)
            else:
                raise pystac.ExtensionTypeError(self._ext_error_message(obj))
        elif not (
            (isinstance(obj, pystac.Collection) and not isinstance(fields, ML_AOI_CollectionFields)) or
            (isinstance(obj, pystac.Item) and not isinstance(fields, ML_AOI_ItemProperties)) or
            (isinstance(obj, pystac.Asset) and not isinstance(fields, ML_AOI_AssetFields)) or
            (isinstance(obj, pystac.Link) and not isinstance(fields, ML_AOI_LinkFields))
        ):
            raise pystac.ExtensionTypeError(
                f"Cannot use {fields.__class__.__name__} with STAC Object {obj.STAC_OBJECT_TYPE}"
            )
        data_json = json.loads(fields.model_dump_json(by_alias=False))
        prop_setter = getattr(self, "_set_property", None) or getattr(self, "_set_summary", None)
        if not prop_setter:
            raise pystac.ExtensionTypeError(
                f"Invalid {self._ext_error_message(self)} implementation "
                f"does not provide any property or summary setter method."
            )
        for field, val in data_json.items():
            prop_setter(field, val)

    @classmethod
    def get_schema_uri(cls) -> str:
        return SCHEMA_URI

    @classmethod
    def has_extension(cls, obj: S):
        ext_uri = cls.get_schema_uri()
        return obj.stac_extensions is not None and any(uri == ext_uri for uri in obj.stac_extensions)

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False) -> "ML_AOI_Extension[T]":
        """
        Extends the given STAC Object with properties from the :stac-ext:`ML-AOI Extension <ml-aoi>`.

        This extension can be applied to instances of :class:`~pystac.Item` or
        :class:`~pystac.Asset`.

        Raises:
            pystac.ExtensionTypeError : If an invalid object type is passed.
        """
        if isinstance(obj, pystac.Collection):
            cls.ensure_has_extension(obj, add_if_missing)
            return cast(ML_AOI_Extension[T], ML_AOI_CollectionExtension(obj))
        elif isinstance(obj, pystac.Item):
            cls.ensure_has_extension(obj, add_if_missing)
            return cast(ML_AOI_Extension[T], ML_AOI_ItemExtension(obj))
        elif isinstance(obj, pystac.Asset):
            cls.ensure_owner_has_extension(obj, add_if_missing)
            return cast(ML_AOI_Extension[T], ML_AOI_AssetExtension(obj))
        # elif isinstance(obj, item_assets.AssetDefinition):
        #     cls.ensure_owner_has_extension(obj, add_if_missing)
        #     return cast(ML_AOI_Extension[T], ItemAssetsML_AOI_Extension(obj))
        else:
            raise pystac.ExtensionTypeError(cls._ext_error_message(obj))

    @classmethod
    def summaries(cls, obj: pystac.Collection, add_if_missing: bool = False) -> "ML_AOI_SummariesExtension":
        """
        Returns the extended summaries object for the given collection.
        """
        cls.ensure_has_extension(obj, add_if_missing)
        return ML_AOI_SummariesExtension(obj)


class ML_AOI_PropertiesExtension(
    PropertiesExtension,
    ML_AOI_Extension[T],
    abc.ABC,
):
    def get_ml_aoi_property(self, prop_name: str, *, _ml_aoi_required: bool = True) -> list[Any]:
        self._retrieve_ml_aoi_property(prop_name, _ml_aoi_required=_ml_aoi_required)
        return self.properties.get(prop_name)

    def set_ml_aoi_property(
        self,
        prop_name: str,
        value: Any,
        *,
        _ml_aoi_required: bool = True,
        pop_if_none: bool = True,
    ) -> None:
        field = self._retrieve_ml_aoi_property(prop_name, _ml_aoi_required=_ml_aoi_required)
        if field:
            # validation must be performed against the non-aliased field
            # then, apply the alias for the actual assignment of the property
            self._validate_ml_aoi_property(prop_name, value)
            prop_name = field.alias or prop_name
        if prop_name in dir(self) or prop_name in self.__annotations__:
            object.__setattr__(self, prop_name, value)
        else:
            super()._set_property(prop_name, value, pop_if_none=pop_if_none)

    def _set_property(
        self, prop_name: str, v: Any, pop_if_none: bool = True
    ) -> None:
        if self._is_ml_aoi_property(prop_name):
            self.set_ml_aoi_property(prop_name, v, _ml_aoi_required=True)
        else:
            super()._set_property(prop_name, v, pop_if_none=pop_if_none)


class ML_AOI_ItemExtension(
    ML_AOI_PropertiesExtension,
    ML_AOI_Extension[pystac.Item],
):
    """
    STAC Item extension for ML-AOI.

    A concrete implementation of :class:`ML_AOI_Extension` on an :class:`~pystac.Item` that extends the properties of
    the Item to include properties defined in the :stac-ext:`ML-AOI Extension <ml-aoi>`.

    This class should generally not be instantiated directly. Instead, call
    :meth:`ML_AOI_Extension.ext` on an :class:`~pystac.Item` to extend it.
    """
    model = ML_AOI_ItemProperties
    item: pystac.Item
    properties: dict[str, Any]

    def __init__(self, item: pystac.Item):
        self.properties = item.properties
        self.item = item

    def get_assets(
        self,
        role: Optional[Union[ML_AOI_Role, List[ML_AOI_Role]]] = None,
        reference_grid: Optional[bool] = None,
        resampling_method: Optional[str] = None,
        media_type: Optional[Union[pystac.MediaType, str]] = None,
        asset_role: Optional[str] = None,
    ) -> dict[str, pystac.Asset]:
        """
        Get the item's assets where ``ml-aoi`` fields are matched.

        Args:
            role: The ML-AOI role, or a list of roles to filter Assets.
                  Note, this should not be confused with Asset 'roles'.
            reference_grid: Filter Assets that contain the specified ML-AOI reference grid value.
            resampling_method: Filter Assets that contain the specified ML-AOI resampling method.
            media_type: Filter Assets with the given media-type.
            asset_role: Filter Assets which contains the specified role (not to be confused with the ML-AOI role).
        Returns:
            Dict[str, Asset]: A dictionary of assets that matched filters.
        """
        # since this method could be used for assets that refer to other extensions as well,
        # filters must not limit themselves to ML-AOI fields
        # if values are 'None', we must consider them as 'ignore' instead of 'any of' allowed values
        return {
            key: asset
            for key, asset in self.item.get_assets(media_type=media_type, role=asset_role).items()
            if (
                not role or
                any(
                    asset_role in (asset.extra_fields.get(add_ml_aoi_prefix("role")) or [])
                    for asset_role in ([role] if isinstance(role, ML_AOI_Role) else role)
                )
            )
            and (
                reference_grid is None or
                asset.extra_fields.get(add_ml_aoi_prefix("reference-grid")) == reference_grid
            )
            and (
                resampling_method is None or
                asset.extra_fields.get(add_ml_aoi_prefix("resampling-method")) == resampling_method
            )
        }

    def __repr__(self) -> str:
        return f"<ML_AOI_ItemExtension Item id={self.item.id}>"


# class ItemAssetsML_AOI_Extension(ML_AOI_Extension[item_assets.AssetDefinition]):
#     """A concrete implementation of :class:`ML_AOI_Extension` on an :class:`~pystac.Asset`
#     that extends the Asset fields to include properties defined in the
#     :stac-ext:`ML-AOI Extension <ml-aoi>`.
#
#     This class should generally not be instantiated directly. Instead, call
#     :meth:`ML_AOI_Extension.ext` on an :class:`~pystac.Asset` to extend it.
#     """
#     properties: dict[str, Any]
#     asset_defn: item_assets.AssetDefinition
#
#     def __init__(self, item_asset: item_assets.AssetDefinition):
#         self.asset_defn = item_asset
#         self.properties = item_asset.properties
#
#     def __repr__(self) -> str:
#         return f"<ML_AOI_AssetExtension Asset href={self.asset_href}>"


class ML_AOI_AssetExtension(
    ML_AOI_PropertiesExtension,
    ML_AOI_Extension[pystac.Asset],
):
    """
    Asset extension for ML-AOI.

    A concrete implementation of :class:`ML_AOI_Extension` on an :class:`~pystac.Asset` that extends the Asset fields to
    include properties defined in the :stac-ext:`ML-AOI Extension <ml-aoi>`.

    This class should generally not be instantiated directly. Instead, call
    :meth:`ML_AOI_Extension.ext` on an :class:`~pystac.Asset` to extend it.
    """
    model = ML_AOI_AssetFields

    asset_href: str
    """
    The ``href`` value of the :class:`~pystac.Asset` being extended.
    """

    properties: dict[str, Any]
    """
    The :class:`~pystac.Asset` fields, including extension properties.
    """

    additional_read_properties: Optional[Iterable[dict[str, Any]]] = None
    """
    If present, this will be a list containing 1 dictionary representing the properties of the owning
    :class:`~pystac.Item`.
    """

    def __init__(self, asset: pystac.Asset):
        self.asset_href = asset.href
        self.properties = asset.extra_fields
        if asset.owner and isinstance(asset.owner, pystac.Item):
            self.additional_read_properties = [asset.owner.properties]

    def __repr__(self) -> str:
        return f"<ML_AOI_AssetExtension Asset href={self.asset_href}>"
    #
    # @property
    # def role(self) -> Optional[ML_AOI_Role]:
    #     return self._get_property(add_ml_aoi_prefix("role"), ML_AOI_Role)
    #
    # @role.setter
    # def role(self, role: ML_AOI_Role) -> None:
    #     self._set_property(add_ml_aoi_prefix("role"), role)
    #
    # @property
    # def reference_grid(self) -> Optional[bool]:
    #     return self._get_property(add_ml_aoi_prefix("reference-grid"), bool)
    #
    # @reference_grid.setter
    # def reference_grid(self, reference_grid: bool) -> None:
    #     self._set_property(add_ml_aoi_prefix("reference-grid"), reference_grid)


class ML_AOI_SummariesExtension(
    SummariesExtension,
    ML_AOI_Extension[pystac.Collection],
):
    """
    Summaries extension for ML-AOI.

    A concrete implementation of :class:`~SummariesExtension` that extends the ``summaries`` field of a
    :class:`~pystac.Collection` to include properties defined in the :stac-ext:`ML-AOI <ml-aoi>`.
    """
    model = ML_AOI_CollectionFields

    collection: pystac.Collection
    summaries: pystac.Summaries

    def __init__(self, collection: pystac.Collection):
        self.collection = collection
        super().__init__(collection)

    def get_ml_aoi_property(
        self,
        prop_name: str,
        *,
        _ml_aoi_required: bool = True,
    ) -> AnySummary:
        field = self._retrieve_ml_aoi_property(prop_name, _ml_aoi_required=_ml_aoi_required)
        if field or _ml_aoi_required:
            prop_name = field.alias or prop_name
            return self.summaries.get_list(prop_name)
        return object.__getattribute__(self, prop_name)

    def set_ml_aoi_property(
        self,
        prop_name: str,
        value: AnySummary,
        pop_if_none: bool = False,
        *,
        _ml_aoi_required: bool = True,
    ) -> None:
        # if _ml_aoi_required and not hasattr(value, "__iter__") or isinstance(value, str):
        #     raise pystac.ExtensionTypeError(
        #         "Summaries value must be an iterable container such as a list, "
        #         f"received '{value.__class__.__name__}' is invalid."
        #     )

        field = self._retrieve_ml_aoi_property(prop_name, _ml_aoi_required=_ml_aoi_required)
        if field or _ml_aoi_required:
            # prop_name = field.alias or prop_name
            if not isinstance(value, (list, pystac.RangeSummary, dict)):
                value = [value]
            self._validate_ml_aoi_property(prop_name, value)
            prop_name = field.alias or prop_name
            super()._set_summary(prop_name, value)
        else:
            object.__setattr__(self, prop_name, value)

    def _set_summary(
        self,
        prop_name: str,
        summaries: Union[list[Any], pystac.RangeSummary[Any], dict[str, Any], None],
    ) -> None:
        if self._is_ml_aoi_property(prop_name):
            self.set_ml_aoi_property(prop_name, summaries, _ml_aoi_required=True)
        else:
            super()._set_summary(prop_name, summaries)


class ML_AOI_CollectionExtension(
    ML_AOI_SummariesExtension,
    ML_AOI_Extension[pystac.Collection]
):
    model = ML_AOI_CollectionFields

    def __init__(self, collection: pystac.Collection):
        ML_AOI_SummariesExtension.__init__(self, collection)
        self.collection = collection
        self.properties = collection.extra_fields
        self.collection.set_self_href = ML_AOI_CollectionExtension.set_self_href  # override hook

    def __repr__(self) -> str:
        return f"<ML_AOI_CollectionExtension Collection id={self.collection.id}>"

    def set_self_href(self, href: Optional[str]) -> None:
        """
        Sets the absolute HREF that is represented by the ``rel == 'self'`` :class:`~pystac.Link`.

        Adds the relevant ML-AOI role applicable for the Collection.
        """
        pystac.Collection.set_self_href(self.collection, href)
        ml_aoi_split = self.get_ml_aoi_property("split")
        if not ml_aoi_split:
            return
        for link in self.collection.links:
            if link.rel == pystac.RelType.SELF:
                field_name = add_ml_aoi_prefix("split")
                link.extra_fields[field_name] = ml_aoi_split[0]


class ML_AOI_ExtensionHooks(ExtensionHooks):
    schema_uri: str = SCHEMA_URI
    prev_extension_ids = {
        ML_AOI_SCHEMA_ID,
        *[uri for uri in SCHEMA_URIS if uri != SCHEMA_URI],
    }
    stac_object_types = {
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


ML_AOI_EXTENSION_HOOKS: ExtensionHooks = ML_AOI_ExtensionHooks()
