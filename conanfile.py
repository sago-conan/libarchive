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
        "enable_nettle": [True, False],
        "enable_openssl": [True, False],
        "enable_lz4": [True, False],
        "enable_lzo": [True, False],
        "enable_lzma": [True, False],
        "enable_zlib": [True, False],
        "enable_bzip2": [True, False],
        "enable_libxml2": [True, False],
        "enable_expat": [True, False],
        "enable_pcreposix": [True, False],
        "enable_libgcc": [True, False],
        "enable_cng": [True, False],
        "enable_tar": [True, False],
        "enable_tar_shared": [True, False],
        "enable_cpio": [True, False],
        "enable_cpio_shared": [True, False],
        "enable_cat": [True, False],
        "enable_cat_shared": [True, False],
        "enable_xattr": [True, False],
        "enable_acl": [True, False],
        "enable_iconv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_nettle": True,
        "enable_openssl": True,
        "enable_lz4": True,
        "enable_lzo": False,
        "enable_lzma": True,
        "enable_zlib": True,
        "enable_bzip2": True,
        "enable_libxml2": True,
        "enable_expat": True,
        "enable_pcreposix": True,
        "enable_libgcc": True,
        "enable_cng": True,
        "enable_tar": False,
        "enable_tar_shared": False,
        "enable_cpio": False,
        "enable_cpio_shared": False,
        "enable_cat": False,
        "enable_cat_shared": False,
        "enable_xattr": True,
        "enable_acl": True,
        "enable_iconv": True,
    }
    generators = "cmake_find_package"
    exports_sources = "ios.toolchain.cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # def requirements(self):
    #     if self.options.enable_lzma:
    #         self.requires.add("xz/5.2.4@sago/stable")

    @property
    def _folder_name(self):
        return "libarchive-{}".format(self.version)

    def source(self):
        url = "https://www.libarchive.org/downloads/{}.tar.gz".format(
            self._folder_name)
        tools.get(url)

    def build(self):
        cmake = CMake(self)
        # Build options
        options = [
            "ENABLE_NETTLE", "ENABLE_OPENSSL", "ENABLE_LZ4", "ENABLE_LZO",
            "ENABLE_LZMA", "ENABLE_ZLIB", "ENABLE_BZip2", "ENABLE_LIBXML2",
            "ENABLE_EXPAT", "ENABLE_PCREPOSIX", "ENABLE_LibGCC", "ENABLE_CNG",
            "ENABLE_TAR", "ENABLE_TAR_SHARED", "ENABLE_CPIO",
            "ENABLE_CPIO_SHARED", "ENABLE_CAT", "ENABLE_CAT_SHARED",
            "ENABLE_XATTR", "ENABLE_ACL", "ENABLE_ICONV"
        ]
        for option in options:
            enable = getattr(self.options, option.lower())
            cmake.definitions[option] = "ON" if enable else "OFF"
        # Other options
        cmake.definitions["ENABLE_TEST"] = "OFF"
        cmake.definitions["ENABLE_COVERAGE"] = "OFF"
        cmake.definitions["ENABLE_INSTALL"] = "ON"
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
