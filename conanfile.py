#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, shutil
from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools


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
        "enable_nettle": False,
        "enable_openssl": False,
        "enable_lz4": False,
        "enable_lzo": False,
        "enable_lzma": False,
        "enable_zlib": False,
        "enable_bzip2": False,
        "enable_libxml2": False,
        "enable_expat": False,
        "enable_pcreposix": False,
        "enable_libgcc": False,
        "enable_cng": False,
        "enable_tar": False,
        "enable_tar_shared": False,
        "enable_cpio": False,
        "enable_cpio_shared": False,
        "enable_cat": False,
        "enable_cat_shared": False,
        "enable_xattr": False,
        "enable_acl": False,
        "enable_iconv": False,
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
        # Patch for Android
        search = "INCLUDE_DIRECTORIES(BEFORE ${CMAKE_CURRENT_SOURCE_DIR}/libarchive)\n"
        append = (
            "IF(ANDROID)\n"
            "  INCLUDE_DIRECTORIES(BEFORE ${CMAKE_CURRENT_SOURCE_DIR}/contrib/android/include)\n"
            "ENDIF(ANDROID)\n")
        tools.replace_in_file(
            os.path.join(self._folder_name, "CMakeLists.txt"), search,
            search + append)

    def _build_cmake(self):
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

    def _build_autotools(self):
        build = AutoToolsBuildEnvironment(self)
        args = [
            "--disable-bsdcat", "--disable-bsdcpio", "--disable-bsdtar",
            "--without-xml2"
        ]
        if "fPIC" in self.options and self.options.fPIC:
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        host = None
        vars = None
        if self.settings.os == "Android":
            toolchain = os.path.join(os.environ["ANDROID_HOME"], "ndk-bundle",
                                     "toolchains", "llvm", "prebuilt",
                                     "linux-x86_64", "bin")
            if self.settings.arch == "armv7":
                host = "armv7a-linux-androideabi"
                cmd_prefix = "arm-linux-androideabi"
            vars = {
                "AR":
                os.path.join(toolchain, cmd_prefix + "-ar"),
                "AS":
                os.path.join(toolchain, cmd_prefix + "-as"),
                "CC":
                os.path.join(
                    toolchain,
                    "{}{}-clang".format(host, self.settings.os.api_level)),
                "CXX":
                os.path.join(
                    toolchain, "{}{}-clang++".format(
                        host, self.settings.os.api_level)),
                "LD":
                os.path.join(toolchain, cmd_prefix + "-ld"),
                "RANLIB":
                os.path.join(toolchain, cmd_prefix + "-ranlib"),
                "STRIP":
                os.path.join(toolchain, cmd_prefix + "-strip"),
            }
        elif self.settings.os == "iOS":
            iphoneos = tools.XCRun(self.settings, sdk="iphoneos")
            flags = "-arch armv7 -arch armv7s -arch arm64 -isysroot " + iphoneos.sdk_path
            vars = {
                "AR": iphoneos.ar,
                "CC": iphoneos.cc,
                "CXX": iphoneos.cxx,
                "LD": iphoneos.find("ld"),
                "CFLAGS": flags,
                "CXXFLAGS": flags,
            }
        build.configure(
            configure_dir=self._folder_name, args=args, host=host, vars=vars)
        build.make()
        build.install()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_cmake()
        else:
            self._build_autotools()
