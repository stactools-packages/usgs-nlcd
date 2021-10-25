import logging
import os

import click

from stactools.usgs_nlcd import cog, stac

logger = logging.getLogger(__name__)


def create_usgsnlcd_command(cli):
    """Creates the stactools-usgs-nlcd command line utility."""
    @cli.group(
        "usgsnlcd",
        short_help=("Commands for working with stactools-usgs-nlcd"),
    )
    def usgsnlcd():
        pass

    @usgsnlcd.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="Path to an output file for the collection",
    )
    def create_collection_command(destination: str):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)
        collection.validate()

        collection.save_object()

        return None

    @usgsnlcd.command("create-item", short_help="Create a STAC item")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output file for the item",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Path to an input COG",
    )
    def create_item_command(source: str, destination: str):
        """Creates a STAC Item

        Args:
            source (str): Path to the COG asset.
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)
        item.validate()

        item.save_object(dest_href=destination)

        return None

    @usgsnlcd.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the COG",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Path to an input GeoTiff",
    )
    @click.option(
        "-t",
        "--tile",
        help="Tile the tiff into many smaller files.",
        is_flag=True,
        default=False,
    )
    def create_cog_command(destination: str, source: str, tile: bool) -> None:
        """Generate a COG from an img/ige file. The COG will be saved in the desination
        with `_cog.tif` appended to the name.
        Args:
            destination (str): Local directory to save output COGs
            source (str, optional): An input USGS-NLCD img file (with the matching ige
            file in the same folder)
            tile (bool, optional): Tile the tiff into many smaller files.
        """
        create_cog_command_fn(destination, source, tile)

    def create_cog_command_fn(destination: str, source: str,
                              tile: bool) -> None:
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        if tile:
            cog.create_retiled_cogs(source, destination)
        else:
            output_path = os.path.join(destination,
                                       os.path.basename(source)[:-4] + ".tif")
            cog.create_cog(source, output_path)

    return usgsnlcd
