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
    settings = "os", "compiler", "arch"
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
        # Set postfix for debug library
        cmake.definitions["CMAKE_DEBUG_POSTFIX"] = "d"
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
        os.mkdir(".build")
        # Build debug & release
        if cmake.is_multi_configuration:
            cmake.configure(
                source_folder=self._folder_name, build_folder=".build")
            for config in ("Debug", "Release"):
                self.output.info("Building {}".format(config))
                cmake.build_type = config
                cmake.build()
        else:
            for config in ("Debug", "Release"):
                self.output.info("Building {}".format(config))
                cmake.build_type = config
                cmake.configure(
                    source_folder=self._folder_name, build_folder=".build")
                cmake.build()
                shutil.rmtree(".build/CMakeFiles")
                os.remove(".build/CMakeCache.txt")
