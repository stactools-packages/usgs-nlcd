import logging
import os.path
import re
from datetime import datetime
from typing import Any, List, Optional

import fsspec
import rasterio
from pyproj import CRS, Proj
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (
    LabelClasses,
    LabelExtension,
    LabelTask,
    LabelType,
)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from stactools.core.io import ReadHrefModifier

from stactools.usgs_nlcd.constants import (
    CLASSIFICATION_VALUES,
    DELTA_DICT,
    DESCRIPTION,
    LICENSE,
    LICENSE_LINK,
    NLCD_CRS_WKT,
    NLCD_EPSG,
    NLCD_ID,
    NLCD_PROVIDER,
    SPATIAL_EXTENT,
    SPATIAL_RES,
    TEMPORAL_EXTENT,
    THUMBNAIL_HREF,
    TITLE,
)

logger = logging.getLogger(__name__)


def create_item(
    cog_href: str,
    cog_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Creates a STAC Item
    Args:
        cog_href (str): Path to COG asset.
            The COG should be created in advance using `cog.create_cog`
        cog_href_modifier (ReadHrefModifier, optional): Modifier for access to cog_href
    Returns:
        Item: STAC Item object
    """
    if cog_href_modifier is not None:
        cog_access_href = cog_href_modifier(cog_href)
    else:
        cog_access_href = cog_href

    match = re.match(
        r"nlcd_(\d\d\d\d)_land_cover_l48_(\d*)_(\d\d)_(\d\d)\.tif",
        os.path.basename(cog_href))
    if match is not None:
        year_str, pub_date, tile1, tile2 = match.groups()
        id = f"{NLCD_ID}-{year_str}-{tile1}-{tile2}"
    else:
        match = re.match(r"nlcd_(\d\d\d\d)_land_cover_l48_(\d*)\.tif",
                         os.path.basename(cog_href))
        if match is None:
            raise ValueError(
                "Could not extract necessary values from {cog_href}")
        year_str, pub_date = match.groups()
        id = f"{NLCD_ID}-{year_str}"

    metadata_url = f"nlcd_{year_str}_land_cover_l48_{pub_date}.xml"

    title = f"USGS-NLCD-{year_str}"

    properties = {"title": title, "description": DESCRIPTION}

    start_datetime = datetime(int(year_str), 1, 1)
    end_datetime = DELTA_DICT[int(year_str)]

    with rasterio.open(cog_access_href) as dataset:
        cog_bbox = list(dataset.bounds)
        cog_transform = list(dataset.transform)
        cog_shape = [dataset.height, dataset.width]

        transformer = Proj.from_crs(CRS.from_epsg(NLCD_EPSG),
                                    CRS.from_epsg(4326),
                                    always_xy=True)
        bbox = list(
            transformer.transform_bounds(dataset.bounds.left,
                                         dataset.bounds.bottom,
                                         dataset.bounds.right,
                                         dataset.bounds.top))
    geom = {
        "type":
        "Polygon",
        "coordinates": [[[bbox[0], bbox[1]], [bbox[2], bbox[1]],
                         [bbox[2], bbox[3]], [bbox[0], bbox[3]],
                         [bbox[0], bbox[1]]]]
    }
    # Create the item
    item = Item(id=id,
                properties=properties,
                geometry=geom,
                bbox=bbox,
                datetime=start_datetime,
                stac_extensions=[])

    item.common_metadata.start_datetime = start_datetime
    item.common_metadata.end_datetime = end_datetime

    # Projection Extension
    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = NLCD_EPSG
    item_projection.wkt2 = NLCD_CRS_WKT

    item_projection.bbox = cog_bbox
    item_projection.transform = cog_transform
    item_projection.shape = cog_shape

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
        "metadata",
        Asset(
            href=metadata_url,
            media_type=MediaType.XML,
            roles=["metadata"],
            title="USGS-NLCD extended metadata",
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
    with fsspec.open(cog_access_href) as file:
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
    cog_asset_projection.wkt2 = item_projection.wkt2
    cog_asset_projection.bbox = item_projection.bbox
    cog_asset_projection.transform = item_projection.transform
    cog_asset_projection.shape = item_projection.shape

    return item


def create_collection(thumbnail_url: str = THUMBNAIL_HREF) -> Collection:
    """Create a STAC Collection.
    Returns:
        Collection: pystac collection object
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
            media_type=MediaType.PNG,
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
            "proj:epsg":
            collection_proj.epsg[0]
        }),
    }

    collection.add_link(LICENSE_LINK)

    return collection
