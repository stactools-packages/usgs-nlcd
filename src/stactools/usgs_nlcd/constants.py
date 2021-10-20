from datetime import datetime

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

NLCD_ID = "USGS_NLCD"
NLCD_EPSG = 4326
NLCD_CRS = CRS.from_epsg(NLCD_EPSG)
LICENSE = "proprietary"
lic_link = """"https://github.com/stactools-packages/usgs-nlcd/tree/main/src/stactools/usgs_nlcd/license
/license.txt"""
LICENSE_LINK = Link(rel="license",
                    target=lic_link,
                    title="Public Domain License - USGS")
SPATIAL_EXTENT = [-130.2, 21.7, -63.7, 49.1]
TEMPORAL_EXTENT = [datetime(2001, 1, 1), datetime(2019, 1, 1) or None]
SPATIAL_RES = 30
THUMBNAIL_HREF = "https://www.mrlc.gov/sites/default/files/2019-04/Land_cover_L48_6.png"
DESCRIPTION = """The National Land Cover Database (NLCD) is an operational land cover monitoring program providing updated land cover and related information for the United States at five-year intervals."""  # noqa E501
TITLE = 'USGS NLCD (CONUS) All Years'
NLCD_PROVIDER = Provider(
    name="United States Geological Survey",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
    url="https://www.mrlc.gov/data/nlcd-land-cover-conus-all-years")

CLASSIFICATION_VALUES = {
    0: "no data",
    11: "Open Water",
    12: "Perennial Ice/Snow",
    21: "Developed, Open Space",
    22: "Developed, Low Intensity",
    23: "Developed, Medium Intensity",
    24: "Developed, High Intensity",
    31: "Barren Land(Rock/Sand/Clay)",
    41: "Deciduous Forest",
    42: "Evergreen Forest",
    43: "Mixed Forest",
    51: "Dwarf Scrub",
    52: "Shrub/Scrub",
    71: "GrassLand/Herbaceous",
    72: "Sedge/Herbaceous",
    73: "Lichens",
    74: "Moss",
    81: "Pasture/Hay",
    82: "Cultivated Crops",
    90: "Woody Wetlands",
    95: "Emergent Herbaceous Wetlands"
}
