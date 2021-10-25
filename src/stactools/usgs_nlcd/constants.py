from datetime import datetime

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

NLCD_ID = "USGS_NLCD"
NLCD_EPSG = 6350
NLCD_CRS = CRS.from_epsg(NLCD_EPSG)
NLCD_CRS_WKT = CRS.from_epsg(NLCD_EPSG).to_wkt()
LICENSE = "proprietary"
lic_link = "https://www.usgs.gov/core-science-systems/hdds/data-policy"
LICENSE_LINK = Link(rel="license",
                    target=lic_link,
                    title="Public Domain Waiver - USGS")
SPATIAL_EXTENT = [-130.2, 21.7, -63.7, 49.1]
TEMPORAL_EXTENT = [datetime(2001, 1, 1) or None, datetime(2019, 1, 1)]
SPATIAL_RES = 30
THUMBNAIL_HREF = "https://www.mrlc.gov/sites/default/files/2019-04/Land_cover_L48_6.png"
DESCRIPTION = "The National Land Cover Database (NLCD) is an operational land cover monitoring program providing updated land cover and related information for the United States at five-year intervals."  # noqa E501
TITLE = 'USGS NLCD (CONUS) All Years'
NLCD_PROVIDER = Provider(
    name="United States Geological Survey",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
    url="https://www.mrlc.gov/data/nlcd-land-cover-conus-all-years")

DELTA_DICT = {
    2001: datetime(2003, 12, 31),
    2004: datetime(2005, 12, 31),
    2006: datetime(2007, 12, 31),
    2008: datetime(2010, 12, 31),
    2011: datetime(2012, 12, 31),
    2013: datetime(2015, 12, 31),
    2016: datetime(2018, 12, 31),
    2019: datetime(2021, 12, 31),
}

NO_DATA = 0
CLASSIFICATION_VALUES = {
    NO_DATA: "no data",
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
TILING_PIXEL_SIZE = (10000, 10000)
