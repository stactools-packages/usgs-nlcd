[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/usgs-nlcd/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools-usgs-nlcd

- Name: usgs-nlcd
- Package: `stactools.usgs_nlcd`
- PyPI: https://pypi.org/project/stactools-usgs-nlcd/
- Owner: @sparkgeo
- Dataset homepage: http://example.com
- STAC extensions used:
  - [file](https://github.com/stac-extensions/file/)
  - [item_assets](https://github.com/stac-extensions/item_assets/)
  - [label](https://github.com/stac-extensions/label/)
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)

## United States Geological Survey - National Land Cover Database (USGS-NLCD)

This stactools-package contains classified land cover data for the lower 48 United States, with a spatial resolution of 30m.
It spans from 2001 - 2019, with updates every ~2-3 years.

## Using the CLI

```
# Create a STAC Collection
stac usgsnlcd create-collection -d "/path/to/collection"
# ...creates "/path/to/collection.json"

# Create a STAC Item from the above COG
stac usgsnlcd create-item "/nlcd_2019_land_cover_l48_20210604_05_09.tif" "/path/to/directory"
# ...creates "/path/to/directory/nlcd_2019_land_cover_l48_20210604_05_09.json"
```

## As a python module

```
from stactools.usgs_nlcd import stac

# Create a STAC Collection

collection = stac.create_collection()

# Create a STAC Item
item = stac.create_item("/path/to/nlcd_cog_tile.tif")
```
