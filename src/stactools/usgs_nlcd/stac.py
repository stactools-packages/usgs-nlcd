import logging
import os.path
from datetime import datetime
from typing import Any, List

import fsspec
import rasterio
from pystac import (Asset, CatalogType, Collection, Extent, Item, MediaType,
                    SpatialExtent, TemporalExtent)
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (LabelClasses, LabelExtension, LabelTask,
                                     LabelType)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (DataType, RasterBand, RasterExtension,
                                      Sampling)

from stactools.usgs_nlcd.constants import (CLASSIFICATION_VALUES, DESCRIPTION,
                                           LICENSE, LICENSE_LINK, NLCD_EPSG,
                                           NLCD_ID, NLCD_PROVIDER,
                                           SPATIAL_EXTENT, SPATIAL_RES,
                                           TEMPORAL_EXTENT, THUMBNAIL_HREF,
                                           TITLE)

logger = logging.getLogger(__name__)


def create_item(source_href: str,
                cog_href: str,
                thumbnail_url: str = THUMBNAIL_HREF) -> Item:
    """Creates a STAC Item
    Args:
        source_href (str): Path to the unaltered source img file.
        cog_href (str): Path to COG asset.
        The COG should be created in advance using `cog.create_cog`
        destination (str): Directory where the Item will be stored.
    Returns:
        Item: STAC Item object
    """

    file_name = os.path.basename(source_href).split("_")[1]
    item_year = datetime.strptime(file_name, '%Y')
    title = f"USGS-NLCD-{item_year}"

    properties = {"title": title, "description": DESCRIPTION}

    geom = {
        "type":
        "Polygon",
        "coordinates": [[[-130.2, 21.7], [-63.7, 21.7], [-63.7, 49.1],
                         [-130.2, 49.1], [-130.2, 21.7]]]
    }

    item = Item(id=f"{NLCD_ID}-{item_year}",
                properties=properties,
                geometry=geom,
                bbox=SPATIAL_EXTENT,
                datetime=item_year,
                stac_extensions=[])

    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = NLCD_EPSG
    if cog_href is not None:
        with rasterio.open(cog_href) as dataset:
            item_projection.bbox = list(dataset.bounds)
            item_projection.transform = list(dataset.transform)
            item_projection.shape = [dataset.height, dataset.width]

    item_label = LabelExtension.ext(item, add_if_missing=True)
    item_label.label_type = LabelType.RASTER
    item_label.label_tasks = [LabelTask.CLASSIFICATION]
    item_label.label_properties = None
    item_label.label_description = ""
    item_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    # Add an asset to the item (COG for example)
    cog_asset = Asset(
        href=cog_href,
        media_type=MediaType.COG,
        roles=[
            "data",
            "labels",
            "labels-raster",
        ],
        title="USGS Land cover COG",
    )
    item.add_asset("landcover", cog_asset)

    item.add_asset(
        "thumbnail",
        Asset(
            href=thumbnail_url,
            media_type=MediaType.JPEG,
            roles=["thumbnail"],
            title="USGS Land Cover thumbnail",
        ),
    )
    # File Extension
    cog_asset_file = FileExtension.ext(cog_asset, add_if_missing=True)
    # The following odd type annotation is needed
    mapping: List[Any] = [{
        "values": [value],
        "summary": summary
    } for value, summary in CLASSIFICATION_VALUES.items()]
    cog_asset_file.values = mapping
    with fsspec.open(cog_href) as file:
        size = file.size
        if size is not None:
            cog_asset_file.size = size
    # Raster Extension
    cog_asset_raster = RasterExtension.ext(cog_asset, add_if_missing=True)
    cog_asset_raster.bands = [
        RasterBand.create(nodata=0,
                          sampling=Sampling.AREA,
                          data_type=DataType.UINT8,
                          spatial_resolution=SPATIAL_RES)
    ]
    # Projection Extension
    cog_asset_projection = ProjectionExtension.ext(cog_asset,
                                                   add_if_missing=True)
    cog_asset_projection.epsg = item_projection.epsg
    cog_asset_projection.bbox = item_projection.bbox
    cog_asset_projection.transform = item_projection.transform
    cog_asset_projection.shape = item_projection.shape
    # Label Extension (doesn't seem to handle Assets properly)
    cog_asset.extra_fields["label:type"] = item_label.label_type
    cog_asset.extra_fields["label:tasks"] = item_label.label_tasks
    cog_asset.extra_fields["label:properties"] = item_label.label_properties
    cog_asset.extra_fields["label:description"] = item_label.label_description
    cog_asset.extra_fields["label:classes"] = [
        item_label.label_classes[0].to_dict()
    ]

    return item


def create_collection(thumbnail_url: str = THUMBNAIL_HREF) -> Collection:
    """Create a STAC Collection.
    Returns:
        pystac.Collection: pystac collection object
    """
    extent = Extent(
        SpatialExtent([SPATIAL_EXTENT]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=NLCD_ID,
        title=TITLE,
        description=DESCRIPTION,
        license=LICENSE,
        providers=[NLCD_PROVIDER],
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    collection.add_asset(
        "thumbnail",
        Asset(
            href=thumbnail_url,
            media_type=MediaType.JPEG,
            roles=["thumbnail"],
            title="USGS Land Cover thumbnail",
        ),
    )

    collection_label = LabelExtension.summaries(collection,
                                                add_if_missing=True)
    collection_label.label_type = [LabelType.RASTER]
    collection_label.label_tasks = [LabelTask.CLASSIFICATION]
    collection_label.label_properties = None
    collection_label.label_classes = [
        # TODO: The STAC Label extension JSON Schema is incorrect.
        # https://github.com/stac-extensions/label/pull/8
        # https://github.com/stac-utils/pystac/issues/611
        # When it is fixed, this should be None, not the empty string.
        LabelClasses.create(list(CLASSIFICATION_VALUES.values()), "")
    ]

    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [NLCD_EPSG]

    collection_item_assets = ItemAssetsExtension.ext(collection,
                                                     add_if_missing=True)

    collection_item_assets.item_assets = {
        "thumbnail":
        AssetDefinition(
            dict(
                type=MediaType.JPEG,
                roles=["thumbnail"],
                title="USGS Land Cover thumbnail",
            )),
        "landcover":
        AssetDefinition({
            "type":
            MediaType.COG,
            "roles": [
                "data",
                "labels",
                "labels-raster",
            ],
            "title":
            "USGS Land Cover COG",
            "raster:bands": [
                RasterBand.create(nodata=0,
                                  sampling=Sampling.AREA,
                                  data_type=DataType.UINT8,
                                  spatial_resolution=SPATIAL_RES).to_dict()
            ],
            "file:values": [{
                "values": [value],
                "summary": summary
            } for value, summary in CLASSIFICATION_VALUES.items()],
            "label:type":
            collection_label.label_type[0],
            "label:tasks":
            collection_label.label_tasks,
            "label:properties":
            None,
            "label:classes": [collection_label.label_classes[0].to_dict()],
            "proj:epsg":
            collection_proj.epsg[0]
        }),
    }

    collection.add_link(LICENSE_LINK)

    return collection
