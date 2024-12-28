"""fluiddocset utility: Generate docsets compatible with Zeal and Dash
======================================================================
Docset is an easy to use offline documentation format. Different applications
such as Zeal (Linux, Windows) and Dash (Mac OS) are available to load such
docsets.  Read more about generating docsets `here
<https://kapeli.com/docsets#python>`_.

.. autofunction::  check_sphinx_build

.. autofunction::  doc_to_docsets

"""
from __future__ import print_function

import importlib
import os
from shlex import split
import shutil
import argparse
from subprocess import call

try:
    from doc2dash.__main__ import main as doc2dash
    from click.testing import CliRunner
except ImportError:
    print("Install doc2dash to use this tool.")

from fluiddyn.io import stdout_redirected


def check_sphinx_build(pkg_name, verbose=True, regenerate=True):
    """Check if Sphinx docs has been built. If not build and return path to
    generated html.

    Parameters
    ----------
    pkg_name : str
        Name of a FluidDyn package.

    Returns
    -------
    str

    """
    pkg = importlib.import_module(pkg_name)
    doc_src = os.path.abspath(
        os.path.join(os.path.dirname(pkg.__file__), "../doc")
    )
    doc_build = os.path.join(doc_src, "_build/html")
    if not os.path.exists(doc_build) or regenerate:
        print("Generating Sphinx documentation ...")
        os.chdir(doc_src)
        cmd = (
            "sphinx-build -b html -d _build/doctrees "
            # We use this because sphinx_rtd_theme
            # does not have a nosidebar option
            "-D html_theme=classic "
            "-D html_theme_options.nosidebar=True "
            ". _build/html"
        )
        print(cmd)
        cmd = split(cmd)
        call(cmd)

    return doc_src, doc_build


def doc_to_docsets(pkg_name="fluiddyn", verbose=False, archive=False):
    """Convert Sphinx docs to docsets and install them.

    Parameters
    ----------
    pkg_name : str
        Name of the Python package.

    verbose : bool
        Verbose output messages.

    archive : bool
        To make an archive or install locally.

    """
    if archive:
        doc_dest = os.getcwd()
    else:
        doc_dest = os.path.expanduser("~/.local/share/Zeal/Zeal/docsets")
        os.makedirs(doc_dest, exist_ok=True)

    doc_src, doc_build = check_sphinx_build(pkg_name, verbose)
    docset_name = pkg_name.title()

    runner = CliRunner()
    cmd = "doc2dash -n {} -d {} -f -v -u https://{}.readthedocs.io ".format(
        docset_name, doc_dest, pkg_name
    )

    icon = os.path.join(doc_src, "icon.png")
    if os.path.exists(icon):
        cmd += "-i {} ".format(icon)

    cmd += doc_build
    print(cmd)
    cmd = split(cmd)
    result = runner.invoke(doc2dash, args=cmd[1:])

    if archive:
        doc_archive = os.path.abspath(os.path.join(doc_dest, docset_name))
        doc_format = ("gztar", ".tar.gz")
        doc_dest = os.path.join(doc_dest, docset_name + ".docset")

        # Make tarball and remove directory generated by doc2dash
        shutil.make_archive(doc_archive, doc_format[0], doc_dest)
        shutil.rmtree(doc_dest)
        doc_dest = doc_archive + doc_format[1]
    else:
        doc_dest = os.path.join(doc_dest, docset_name + ".docset")

    if verbose:
        print(result.output)

    print("Docset generated at", doc_dest)


def main():
    """Parse arguments and execute."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("package", help="Name of a FluidDyn package", type=str)

    parser.add_argument(
        "-a",
        "--archive",
        help="Do not install to home directory, only create a zip file.",
        action="store_true",
    )

    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    doc_to_docsets(args.package, args.verbose, args.archive)


if __name__ == "__main__":
    main()