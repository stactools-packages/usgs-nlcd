import os.path
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.usgs_nlcd.commands import create_usgsnlcd_command


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_usgsnlcd_command]

    def test_create_collection(self):
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-collection command and validate

            # Example:
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(
                ["usgsnlcd", "create-collection", "-d", destination])

            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(destination)
            self.assertEqual(collection.id, "usgs-nlcd")

            collection.validate()

    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:

            # Example:
            destination = os.path.join(tmp_dir, "collection.json")
            result = self.run_command([
                "usgsnlcd",
                "create-item",
                "-s",
                "tests/data-files/nlcd_2019_land_cover_l48_20210604_05_09.tif",
                "-d",
                destination,
            ])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(destination)
            self.assertEqual(item.id, "usgs-nlcd-2019-05-09")

            item.validate()
