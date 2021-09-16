import logging

import click

from stactools.usgs_nlcd import stac

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
    @click.argument("destination")
    def create_collection_command(destination: str):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

        return None

    @usgsnlcd.command("create-item", short_help="Create a STAC item")
    @click.argument("source_href")
    @click.argument("cog_href")
    @click.argument("destination")
    def create_item_command(source_href: str, cog_href: str, destination: str):
        """Creates a STAC Item

        Args:
            source_href (str): Path to the unaltered source img file.
            cog_href (str): Path to the COG asset.
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source_href, cog_href)

        item.save_object(dest_href=destination)

        return None

    return usgsnlcd
