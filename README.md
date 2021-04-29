# STAC ML AOI Extension

- **Title:** ML AOI
- **Identifier:** <https://stac-extensions.github.io/ml-aoi/v1.0.0/schema.json>
- **Field Name Prefix:** ml-aoi
- **Scope:** Item, Collection
- **Extension [Maturity Classification](https://github.com/radiantearth/stac-spec/tree/master/extensions/README.md#extension-maturity):** Proposal
- **Owner**: @jisantuc

This document explains the ML AOI Extension to the [SpatioTemporal Asset Catalog](https://github.com/radiantearth/stac-spec) (STAC) specification.

An Item and Collection extension to provide labeled training data for machine learning models.
This extension relies on but is distinct from existing `label` extension.
STAC items using `label` extension link label assets with the source imagery for which they are valid, often as result of human labelling effort.
By contrast STAC items using `ml-aoi` extension link label assets with raster items for each specific machine learning model is being trained.

In addition to linking labels with feature items the `ml-aoi` extension addresses some of the common configurations for ML workflows.
The use of this extension is intended to make model training process reproducible as well as providing model provenance once the model is trained.

## Item Properties and Collection Fields

| Field Name           | Type                      | Description |
| -------------------- | ------------------------- | ----------- |
| `ml-aoi:split`       | string                    | Assigns item to one of `train`, `test`, or `validate` sets |

### Additional Field Information

#### ml-aoi:split

This field is optional. If not provided, its expected that the split property will be added later before consuming the items.

#### bbox and geometry

* `ml-aoi` Multiple items may reference the same label and image item by scoping the `bbox` and `geometry` fields. TODO: Better describe scoping of overlap between raster and label items?
* `ml-aoi` Items `bbox` field may overlap when they belong to different `ml-aoi:split` set.
* `ml-aoi` Items in the same Collection should never have overlapping `geometry` fields.

## Links

`ml-aoi` Item must link to both label and raster STAC items valid for its area of interest.
These Link objects should set `rel` field to `derived_from` for both label and feature items.

`ml-aoi` Item should be contain enough metadata to make it consumable without the need for following the label and feature link item links. In reality this may not be practical because the use-case may not be fully known at the time the Item is generated. Therefore it is critical that source label and feature items are linked to provide the future consumer the option to collect additional metadata from them.

| Field Name    | Type   | Name | Description                 |
| ------------- | ------ | ---- | --------------------------- |
| `ml-aoi:role` | string | Role | `label` or `feature`        |

### Labels

An `ml-aoi` Item must link to exactly one STAC item that is using `label` extension.
Label links should provide `ml-aoi:role` field set to `label` value.

### Features

An `ml-aoi` Item must link to at least one raster STAC item.
Feature links should provide `ml-aoi:role` field set to `feature` value.

Linked feature STAC items may use `eo` but that is not required.
It is up to the consumer of `ml-aoi` Items to decide how to use the linked feature rasters.

## Assets

Item should directly include assets for label and feature rasters.

| Field Name                 | Type   | Name              | Description                                  |
| -------------------------- | ------ | ----------------- | -------------------------------------------- |
| `ml-aoi:role`              | string | Role              | `label` or `feature`                  |
| `ml-aoi:reference-grid`    | bool   | Reference Grid    | This raster provides reference pixel grid for model training |
| `ml-aoi:resampling-method` | string | Resampling Method | Resampling method for non-reference-grid feature rasters        |

Resampling method should be one of the values [supported by gdalwarp](https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-r)

### Labels

Assets for the label item can be copied directly from the label item with their asset name preserved.
Label assets should provide `ml-aoi:role` field set to `label` value.

### Features

Assets for the raster item can be copied directly from the label item with their asset name preserved.
Feature assets should provide `ml-aoi:role` field set to `feature` value.

When multiple raster features are included their resolutions and pixel grids are not likely to align.
One raster may be specify `ml-aoi:reference-grid` field set to `true` to indicate that all other features
should be resampled to match its pixel grid during model training.
Other raster assets should be resampled to the reference pixel grid.

## Collection

All `ml-aoi` Items should belong to a Collection that designates a specific model training input.
There is one-to-one mapping between a single ml-aoi collection and a machine-learning model.

### Collection fields

The consumer of `ml-aoi` catalog needs to understand the available label classes and features without crawling the full catalog.
When member Items include multiple feature rasters it is possible that not all of them will overlap every AOI.

## Contributing

All contributions are subject to the
[STAC Specification Code of Conduct](https://github.com/radiantearth/stac-spec/blob/master/CODE_OF_CONDUCT.md).
For contributions, please follow the
[STAC specification contributing guide](https://github.com/radiantearth/stac-spec/blob/master/CONTRIBUTING.md) Instructions
for running tests are copied here for convenience.

### Running tests

The same checks that run as checks on PR's are part of the repository and can be run locally to verify that changes are valid. 
To run tests locally, you'll need `npm`, which is a standard part of any [node.js installation](https://nodejs.org/en/download/).

First you'll need to install everything with npm once. Just navigate to the root of this repository and on 
your command line run:
```bash
npm install
```

Then to check markdown formatting and test the examples against the JSON schema, you can run:
```bash
npm test
```

This will spit out the same texts that you see online, and you can then go and fix your markdown or examples.

If the tests reveal formatting problems with the examples, you can fix them with:
```bash
npm run format-examples
```

# Design Decisions

Central choices and rational behind them is outlined in the ADR format:

| ID   | ADR |
|------|-----|
| 0002 | [Use Case](docs/0002-use-case-definition.md) |
| 0003 | [Test/Train/Validation Split](docs/0003-test-train-validation-split.md) |
| 0004 | [Sourcing Multiple Label Items](docs/0004-multiple-label-items.md) |
