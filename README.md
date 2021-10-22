# United States Geological Survey - National Land Cover Database (USGS-NLCD)

This stactools-package contains classified land cover data for the lower 48 United States, with a spatial resolution of 30m.
It spans from 2001 - 2019, with updates every ~2-3 years. 


# Usage

As a python module
```
from stactools.usgs_nlcd import stac

# Create a STAC Collection

collection = stac.create_collection()

# Create a STAC Item
item = stac.create_item("/path/to/nlcd_cog_tile.tif")
```
# Using the CLI
```
# Create a STAC Collection
stac usgsnlcd create-collection -d "/path/to/collection"
# ...creates "/path/to/collection.json"

# Create a STAC Item from the above COG
stac usgsnlcd create-item "/nlcd_2019_land_cover_l48_20210604_05_09.tif" "/path/to/directory"
# ...creates "/path/to/directory/nlcd_2019_land_cover_l48_20210604_05_09.json"
```
