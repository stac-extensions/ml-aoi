---
id: 0003-multiple-label-items
title: 1 - Multiple Label Items
---
Date: 2020-08-11

## Status

Proposed

## Context

Should each `ml-aoi` Item be able to bring in multiple labels?
This would be a useful feature for training multi-class classifiers.
One can imagine having a label STAC item for buildings and separate STAC item for fields.
STAC Items Links object is an array, so many label items could be linked to from a single `ml-aoi` STAC Item.

#### Limiting to single label link

Limiting to single label link however is appealing because the label item metadata could be copied over to `ml-aoi` Item.
This would remove the need to follow the link for the label item during processing.
In practice this would make each `ml-aoi` Item also a `label` Item, allowing for its re-use by tooling that understands `label`.

If multi-class label dataset would be required there would have to be a mechanical pre-processing step of combining
existing labels into a single STAC `label` item. This could mean either union of GeoJSON FeatureCollections per item or
a configuration of a more complex STAC `label` Item that links to multiple label assets.

#### Allowing multiple labels

The main appeal of consuming multi-label `ml-aoi` items is that it would allow referencing multiple label sources,
some which could be external, without the need for pre-processing and thus minimizing data duplication.

If multiple labels were to be allowed the `ml-aoi` the pre-processing step above would be pushed into `ml-aoi` consumer.
The consumer would need appropriate metadata in order to decipher how the label structure.
This would require either crawling the full catalog or some kind of meta-label structure that combines the metadata
from all the included labels into a single structure that could be interpreted by the consumer.

## Decision

`ml-aoi` Items should be limited to linking to only a single label item.
Requiring the consumer to interpret multiple label items pushed unreasonable complexity on the user.
Additionally combining labels likely requires series of processing and validation steps.
Each one of those would likely require judgment calls and exceptions.
For instance when combining building and fields label datasets the user should check that no building and field polygons overlap.

It is not realistic to expect all possible requirements of that process to be expressed by a simple metadata structure.
Therefore it is better to explicitly require the label combination as a separate process done by the user.
The resulting label catalog can capture that design and iteration required for that process anyway.

## Consequences

`ml-aoi` Items can copy all `label` extension properties from the `label` Item.
In effect `ml-aoi` Items extends `label` item by adding links to feature imagery.
This formulation lines up with original problem statement for `ml-aoi` extension.