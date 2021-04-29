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

| Field Name  | Type   | Description |
| ----------- | ------ | ----------- |
| x           | number | **REQUIRED**. Describe the required field... |
| y           | number | **REQUIRED**. Describe the required field... |
| z           | number | **REQUIRED**. Describe the required field... |

## Relation types

The following types should be used as applicable `rel` types in the
[Link Object](https://github.com/radiantearth/stac-spec/tree/master/item-spec/item-spec.md#link-object).

| Type                | Description |
| ------------------- | ----------- |
| fancy-rel-type      | This link points to a fancy resource. |

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

# ml-aoi STAC Extension

Central choices and rational behind them is outlined in the ADR format:

| ID   | ADR |
|------|-----|
| 0002 | [Use Case](docs/0002-use-case-definition.md) |
| 0003 | [Test/Train/Validation Split](docs/0003-test-train-validation-split.md) |
| 0004 | [Sourcing Multiple Label Items](docs/0004-multiple-label-items.md) |
