import logging
import os
from glob import glob
from subprocess import CalledProcessError, check_output
from tempfile import TemporaryDirectory

import rasterio

from stactools.usgs_nlcd.constants import TILING_PIXEL_SIZE

logger = logging.getLogger(__name__)


def create_retiled_cogs(
    input_path: str,
    output_directory: str,
    raise_on_fail: bool = True,
    dry_run: bool = False,
) -> str:
    """Split tiff into tiles and create COGs
    Args:
        input_path (str): Path to the USGS NLCD data.
        output_directory (str): The directory to which the COG will be written.
        raise_on_fail (bool, optional): Whether to raise error on failure.
            Defaults to True.
        dry_run (bool, optional): Run without downloading tif, creating COG,
            and writing COG. Defaults to False.
    Returns:
        str: The path to the output COGs.
    """
    output = None
    try:
        if dry_run:
            logger.info(
                "Would have split TIF into tiles, created COGs, and written COGs"
            )
        else:
            with TemporaryDirectory() as tmp_dir:
                cmd = [
                    "gdal_retile.py",
                    "-ps",
                    str(TILING_PIXEL_SIZE[0]),
                    str(TILING_PIXEL_SIZE[1]),
                    "-targetDir",
                    tmp_dir,
                    input_path,
                ]
                try:
                    output = check_output(cmd)
                except CalledProcessError as e:
                    output = e.output
                    raise
                finally:
                    logger.info(f"output: {str(output)}")
                file_names = glob(f"{tmp_dir}/*.tif")
                for f in file_names:
                    input_file = os.path.join(tmp_dir, f)
                    output_file = os.path.join(output_directory,
                                               os.path.basename(f))
                    with rasterio.open(input_file, "r") as dataset:
                        contains_data = dataset.read().any()
                    if contains_data:
                        create_cog(input_file, output_file, raise_on_fail,
                                   dry_run)

    except Exception:
        logger.error("Failed to process {}".format(input_path))

        if raise_on_fail:
            raise

    return output_directory


def create_cog(
    input_path: str,
    output_path: str,
    raise_on_fail: bool = True,
    dry_run: bool = False,
) -> str:
    """Create COG from a tif
    Args:
        input_path (str): Path to the Natural Resources Canada Land Cover data.
        output_path (str): The path to which the COG will be written.
        raise_on_fail (bool, optional): Whether to raise error on failure.
            Defaults to True.
        dry_run (bool, optional): Run without downloading tif, creating COG,
            and writing COG. Defaults to False.
    Returns:
        str: The path to the output COG.
    """

    output = None
    try:
        if dry_run:
            logger.info("Would have read TIF, created COG, and written COG")
        else:
            cmd = [
                "gdal_translate",
                "-of",
                "COG",
                "-co",
                "NUM_THREADS=ALL_CPUS",
                "-co",
                "BLOCKSIZE=512",
                "-co",
                "compress=deflate",
                "-co",
                "LEVEL=9",
                "-co",
                "predictor=yes",
                "-co",
                "OVERVIEWS=IGNORE_EXISTING",
                "-a_nodata",
                "0",
                input_path,
                output_path,
            ]

            try:
                output = check_output(cmd)
            except CalledProcessError as e:
                output = e.output
                raise
            finally:
                logger.info(f"output: {str(output)}")

    except Exception:
        logger.error("Failed to process {}".format(output_path))

        if raise_on_fail:
            raise

    return output_path
