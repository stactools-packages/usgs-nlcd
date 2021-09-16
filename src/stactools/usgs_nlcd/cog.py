import os.path

from stactools.core.utils.convert import cogify


def create_cog(img_href: str, cog_href: str) -> None:
    cog_output = os.path.join(
        os.path.split(cog_href)[0], ('cog' + os.path.split(cog_href)[-1]))
    cogify(img_href, cog_output, ["-co", "compress=LZW", "-a_nodata", "0"])

    print('Done')
