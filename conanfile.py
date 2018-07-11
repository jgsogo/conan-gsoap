

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake, RunEnvironment, MSBuild
from conans.errors import NotFoundException


class ApacheAPR(ConanFile):
    name = "gsoap"  # TODO: Actual name is gSOAP, but may I adhere to @bincrafters claim for lowercase names?
    version_major = "2.8"
    version = version_major + ".68"
    url = "https://github.com/jgsogo/conan-gsoap"
    homepage = "http://www.cs.fsu.edu/~engelen/soap.html"
    license = "http://www.cs.fsu.edu/~engelen/soaplicense.html"
    description = "The gSOAP toolkit is a C and C++ software development toolkit for SOAP and " \
                  "REST XML Web services and generic C/C++ XML data bindings."
    exports_sources = ["LICENSE", ]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    short_paths = True

    lib_name = "gsoap-" + version_major

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("winflexbison/2.5.14@jgsogo/stable")
        else:
            self.requires("bison/3.0.4@bincrafters/stable")
            self.requires("flex/2.6.4@bincrafters/stable")

    def source(self):
        try:
            tools.get("https://sourceforge.net/projects/gsoap2/files/{name}-{version_major}/{name}_{version}.zip/download".format(name=self.name, version_major=self.version_major, version=self.version))
        except NotFoundException:  # Maybe it has been moved to `oldreleases`
            tools.get("https://sourceforge.net/projects/gsoap2/files/oldreleases/{name}_{version}.zip/download".format(name=self.name, version=self.version))

    def _patch_vcxproj(self, vcxproj):
        # MSVC 2015
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionSettings">', r'<ImportGroup Label="ExtensionSettings"><Import Project="..\..\..\..\..\..\..\..\Users\Laura\.conan\data\winflexbison\2.5.14\jgsogo\stable\package\63da998e3642b50bee33f4449826b2d623661505\bin\custom_build_rules\win_flex_bison_custom_build.props" />')
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionTargets">', r'<ImportGroup Label="ExtensionTargets"><Import Project="..\..\..\..\..\..\..\..\Users\Laura\.conan\data\winflexbison\2.5.14\jgsogo\stable\package\63da998e3642b50bee33f4449826b2d623661505\bin\custom_build_rules\win_flex_bison_custom_build.targets" />')
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_lex.l" />', '<Flex Include="soapcpp2_lex.l"><FileType>Document</FileType></Flex>')
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_yacc.y" />', '<Bison Include="soapcpp2_yacc.y"><FileType>Document</FileType></Bison>')

    def build(self):
        if self.settings.os == "Windows":
            with tools.environment_append(RunEnvironment(self).vars):
                self.run("win_flex --version")
                self.run("win_bison --version")
                self.run("win_flex --help")
                self.run("win_bison --help")
                msbuild = MSBuild(self)
                try:
                    print("*"*100)
                    out = msbuild.build(os.path.abspath(os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "soapcpp2", "soapcpp2.sln")),
                                        platforms={'x86': 'Win32'})
                    print(out)
                except Exception as e:
                    print("!" * 100)
                    print(e)
                    print(type(e))
                self._patch_vcxproj(os.path.abspath(
                    os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "soapcpp2", "soapcpp2",
                                 "soapcpp2.vcxproj")))
                out = msbuild.build(os.path.abspath(
                    os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "soapcpp2", "soapcpp2.sln")),
                    upgrade_project=False,
                    platforms={'x86': 'Win32'})
                print(out)
                # soapcpp2_flex = os.path.abspath(os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "soapcpp2", "soapcpp2", "soapcpp2_lex.l"))
                # self.run("win_flex %s" % soapcpp2_flex)
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(configure_dir=self.lib_name, args=['--prefix', self.package_folder, ], build=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        pass

    def package_info(self):
        pass
