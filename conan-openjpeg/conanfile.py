from conans import ConanFile, CMake, tools
import os
import glob


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    url = ""
    version = "2.3.1"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    topics = ("conan", "jpeg2000", "jp2", "openjpeg", "image", "multimedia", "format", "graphics")
    options = {"shared": [True, False], "build_codec": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'build_codec': True, 'fPIC': True}
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD 2-Clause"

    _source_subfolder = "source_subfolder"

    requires =  "zlib/1.2.11", \
                "libtiff/4.0.10@local/stable", \
                "libpng/1.6.37", \
                "lcms/2.9"
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/uclouvain/openjpeg.git", "v{0}".format(self.version))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        cmake.definitions['BUILD_PKGCONFIG_FILES'] = False
        cmake.definitions['CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP'] = True
        cmake.definitions['BUILD_CODEC'] = False
        if self.settings.os == "Linux":
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = True

        libs = ["zlib","libtiff","lcms"]
        lib_names = {}
        for lib in libs:
            if self.settings.os == "Windows":
                lib_names[lib] = self.deps_cpp_info[lib].libs[0] + ".lib"
            else:
                lib_names[lib] = "lib" + self.deps_cpp_info[lib].libs[0] + ".a"

        cmake.definitions['ZLIB_INCLUDE_DIR'] =  self.deps_cpp_info["zlib"].include_paths[0]
        cmake.definitions['ZLIB_LIBRARY'] =  os.path.join(self.deps_cpp_info["zlib"].lib_paths[0], lib_names["zlib"])

        cmake.definitions['TIFF_INCLUDE_DIR'] =  self.deps_cpp_info["libtiff"].include_paths[0]
        cmake.definitions['TIFF_LIBRARY'] =  os.path.join(self.deps_cpp_info["libtiff"].lib_paths[0], lib_names["libtiff"])

        cmake.definitions['LCMS_INCLUDE_DIR'] =  self.deps_cpp_info["lcms"].include_paths[0]
        cmake.definitions['LCMS_LIBRARY'] =  os.path.join(self.deps_cpp_info["lcms"].lib_paths[0], lib_names["lcms"])

        cmake.configure()
        return cmake

    def build(self):
        # ensure that bundled cmake files are not used
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join('include', 'openjpeg-%s.%s' % tuple(self.version.split('.')[0:2])))
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('OPJ_STATIC')
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.name = 'OpenJPEG'
