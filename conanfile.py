#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, shutil
from conans import CMake, ConanFile, tools


class LibarchiveConan(ConanFile):
    name = "libarchive"
    version = "3.3.3"
    license = "New BSD License"
    url = "https://github.com/sago-conan/libarchive"
    homepage = "https://www.libarchive.org/"
    description = "Multi-format archive and compression library."
    settings = "arch", "build_type", "compiler", "os"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_lzma": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "enable_lzma": True}
    generators = "cmake_find_package"
    exports_sources = "ios.toolchain.cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.enable_lzma:
            self.requires.add("xz/5.2.4@sago/stable")

    @property
    def _folder_name(self):
        return "libarchive-{}".format(self.version)

    def source(self):
        url = "https://www.libarchive.org/downloads/{}.tar.gz".format(
            self._folder_name)
        tools.get(url)

    def build(self):
        cmake = CMake(self)
        # Set options
        cmake.definitions[
            "ENABLE_LZMA"] = "ON" if self.options.enable_lzma else "OFF"
        # Cross-compile toolchains
        if self.settings.os == "Android":
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                os.environ["ANDROID_HOME"],
                "ndk-bundle/build/cmake/android.toolchain.cmake")
        elif self.settings.os == "iOS":
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                self.source_folder, "ios.toolchain.cmake")
        self.output.info(cmake.definitions)
        # Build and install
        cmake.configure(source_folder=self._folder_name)
        cmake.build()
        cmake.install()
