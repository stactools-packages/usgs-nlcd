from datetime import datetime
import logging
import os.path
import rasterio

from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.label import (
    LabelClasses,
    LabelExtension,
    LabelTask,
    LabelType,
)
from pystac import (
    Collection,
    Item,
    Asset,
    Extent,
    SpatialExtent,
    TemporalExtent,
    CatalogType,
    MediaType,
)

from stactools.usgs_nlcd.constants import (
    NLCD_ID,
    SPATIAL_EXTENT,
    TEMPORAL_EXTENT,
    NLCD_PROVIDER,
    TITLE,
    DESCRIPTION,
    LICENSE,
    LICENSE_LINK,
    NLCD_EPSG,
    CLASSIFICATION_VALUES
)

logger = logging.getLogger(__name__)

def create_item(source_href: str, cog_href: str) -> Item:
    """Creates a STAC Item
    Args:
        source_href: Path to the unaltered source img file.
        cog_href (str): Path to COG asset.
        The COG should be created in advance using `cog.create_cog`
        destination (str): Directory where the Item will be stored.
    Returns:
        Item: STAC Item object
    """
    
    file_name = os.path.basename(source_href).split("_")[1]
    
    item_year = datetime.strptime(file_name, '%Y')
    title = "USGS-NLCD-" + str(item_year)  + "-LANDCOVER"

    properties = {
        "title": title,
        "description": DESCRIPTION
    }
    
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
    item.add_asset(
        "cog",
        Asset(
            href=cog_href,
            media_type=MediaType.COG,
            roles=["data"],
        ),
    )
    
    return item

def create_collection() -> Collection:
    """Create a STAC Collection using a jsonld file provided by NRCan.
    The metadata dict may be created using `utils.get_metadata`
    Args:
        thumbnail_url (str, optional): URL to a thumbnail image for the Collection
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

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)

    item_assets.item_assets = {
        "cog":
        AssetDefinition({
            "type":
            MediaType.COG,
            "roles": ["data"],
            "description": "NLCD COG"
        })
    }

    collection.add_link(LICENSE_LINK)

    return collection


