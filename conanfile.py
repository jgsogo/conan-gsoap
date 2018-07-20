

import os

from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake, RunEnvironment, MSBuild
from conans.errors import NotFoundException
from conans.tools import os_info, SystemPackageTool, chdir


class GSoap(ConanFile):
    name = "gsoap"  # TODO: Actual name is gSOAP, but may I adhere to @bincrafters claim for lowercase names?
    version_major = "2.8"
    version = version_major + ".68"
    url = "https://github.com/jgsogo/conan-gsoap"
    homepage = "http://www.cs.fsu.edu/~engelen/soap.html"
    license = "http://www.cs.fsu.edu/~engelen/soaplicense.html"
    description = "The gSOAP toolkit is a C and C++ software development toolkit for SOAP and " \
                  "REST XML Web services and generic C/C++ XML data bindings."
    settings = "os", "compiler", "build_type", "arch"
    options = {"with_openssl": [True, False],
               "with_ipv6": [True, False],
               "with_cookies": [True, False],
               "with_c_locale": [True, False]}
    default_options = "with_openssl=True", "with_ipv6=True", \
                      "with_cookies=True", "with_c_locale=True"
    generators = "cmake"
    short_paths = True
    exports_sources = ["LICENSE", "FindGSOAP.cmake", "src/*.cmake", "src/*.txt"]

    lib_name = "gsoap-" + version_major

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("winflexbison/2.5.14@jgsogo/stable")
        else:
            self.requires("bison/3.0.4@bincrafters/stable")
            self.requires("flex/2.6.4@bincrafters/stable")
        if self.options.with_openssl:
            self.requires("OpenSSL/1.0.2o@conan/stable")

    def source(self):
        try:
            tools.get("https://sourceforge.net/projects/gsoap2/files/{name}-{version_major}/{name}_{version}.zip/download".format(name=self.name, version_major=self.version_major, version=self.version))
        except NotFoundException:  # Maybe it has been moved to `oldreleases`
            tools.get("https://sourceforge.net/projects/gsoap2/files/oldreleases/{name}_{version}.zip/download".format(name=self.name, version=self.version))

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.definitions["GSOAP_PATH"] = os.path.join(self.source_folder, self.lib_name).replace('\\', '/')
            if self.options.with_openssl:
                cmake.definitions["WITH_OPENSSL"] = True
                cmake.definitions["WITH_GZIP"] = True
            if self.options.with_ipv6:
                cmake.definitions["WITH_IPV6"] = True
            cmake.definitions["WITH_COOKIES"] = self.options.with_cookies
            cmake.definitions["WITH_C_LOCALE"] = self.options.with_c_locale

            cmake.configure(source_folder="src")
            cmake.build()
            cmake.install()

        else:
            with chdir(self.lib_name):
                self.run('chmod +x configure')
                self.run('./configure --help')
                env_build = AutoToolsBuildEnvironment(self)
                self.run('autoreconf -f -i')  # Fix out of date aclocal
                env_build.configure(args=['--prefix', self.package_folder,
                                          '--with-openssl={}'.format(self.deps_cpp_info["OpenSSL"].rootpath),
                                          '--with-zlib={}'.format(self.deps_cpp_info["zlib"].rootpath),
                                          '--enable-ipv6' if self.options.with_ipv6 else '--disable-ipv6',
                                          '--enable-cookies' if self.options.with_cookies else '--disable-cookies',
                                          '--enable-with_c_locale' if self.options.with_c_locale else '--disable-c_locale',
                                          ],
                                    build=False)
                env_build.make(args=["-j1", ])  # Weird, but with -j2 it fails
                env_build.make(args=['install'])
            """
            self.run('ls -la {}'.format(os.path.join(self.lib_name, 'gsoap', 'bin')))
            with chdir(os.path.join(self.lib_name, 'gsoap', 'src')):
                self.run('make -f MakefileManual')
                # self.run('make install')

            with chdir(os.path.join(self.lib_name, 'gsoap', 'wsdl')):
                self.run('make -f MakefileManual')
                # self.run('make install')
            self.run('ls -la {}'.format(os.path.join(self.lib_name, 'gsoap', 'bin')))
            """

    def package(self):
        self.copy("FindGSOAP.cmake", dst=".", src=".")

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        defines = []
        if self.options.with_openssl:
            libs = ["gsoapssl++", ]
            defines.append("WITH_OPENSSL")
            defines.append("WITH_GZIP")
        else:
            libs = ["gsoap++", ]
        self.cpp_info.libs = libs

        if self.options.with_ipv6:
            defines.append("WITH_IPV6")
        if self.options.with_cookies:
            defines.append("WITH_COOKIES")
        if self.options.with_c_locale:
            defines.append("WITH_C_LOCALE")
        self.cpp_info.defines = defines
