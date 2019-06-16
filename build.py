#!/usr/bin/python
# -*- coding: UTF-8 -*-

from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds()
    builder.remove_build_if(
        lambda build: "compiler.runtime" in build.settings and build.settings["compiler.runtime"].startswith("MT")
    )
    builder.run()
