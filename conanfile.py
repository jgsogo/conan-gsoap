

import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake, RunEnvironment, MSBuild
from conans.errors import NotFoundException
from conans.tools import os_info, SystemPackageTool, chdir


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

    def system_requirements(self):
        if os_info.is_linux:
            pack_name = "autotools-dev automake"
            installer = SystemPackageTool()
            installer.install(pack_name)

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
        props_file = os.path.join(self.deps_cpp_info["winflexbison"].rootpath, "bin", "custom_build_rules", "win_flex_bison_custom_build.props")
        targets_file = os.path.join(self.deps_cpp_info["winflexbison"].rootpath, "bin", "custom_build_rules", "win_flex_bison_custom_build.targets")
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionSettings">', '<ImportGroup Label="ExtensionSettings"><Import Project="{}" />'.format(props_file))
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionTargets">', '<ImportGroup Label="ExtensionTargets"><Import Project="{}" />'.format(targets_file))
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_lex.l" />', '<Flex Include="soapcpp2_lex.l"><FileType>Document</FileType><OutputFile>lex.%(Filename).c</OutputFile></Flex>')
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_yacc.y" />', '<Bison Include="soapcpp2_yacc.y"><FileType>Document</FileType><OutputFile>%(Filename).tab.c</OutputFile></Bison>')

    def build(self):
        if self.settings.os == "Windows":
            # Build soapcpp2.exe
            with tools.environment_append(RunEnvironment(self).vars):
                soapcpp2_dir = os.path.abspath(os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "soapcpp2"))
                soapcpp2_sln = os.path.join(soapcpp2_dir, "soapcpp2.sln")
                msbuild = MSBuild(self)
                try:
                    out = msbuild.build(soapcpp2_sln, platforms={'x86': 'Win32'})
                except Exception as e:
                    pass  # It fails when upgrading
                self._patch_vcxproj(os.path.join(soapcpp2_dir, "soapcpp2", "soapcpp2.vcxproj"))
                out = msbuild.build(soapcpp2_sln, upgrade_project=False, platforms={'x86': 'Win32'})

            # Build wsdl2h.exe
            wsdl2h_dir = os.path.abspath(os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "wsdl2h"))
            # - copy soapcpp2.exe to wsdl2h directory (we want to use what we have compiled)
            shutil.copy2(os.path.join(soapcpp2_dir, str(self.settings.build_type), "soapcpp2.exe"),
                         os.path.join(wsdl2h_dir, "wsdl2h"))
            # - compile it
            wsdl2h_sln = os.path.join(wsdl2h_dir, "wsdl2h.sln")
            msbuild = MSBuild(self)
            out = msbuild.build(wsdl2h_sln, platforms={'x86': 'Win32'})

        else:
            self.run('ls -la {}'.format(os.path.join(self.lib_name, 'gsoap', 'bin')))
            with chdir(os.path.join(self.lib_name, 'gsoap', 'src')):
                self.run('make -f MakefileManual')
                # self.run('make install')

            with chdir(os.path.join(self.lib_name, 'gsoap', 'wsdl')):
                self.run('make -f MakefileManual')
                # self.run('make install')
            self.run('ls -la {}'.format(os.path.join(self.lib_name, 'gsoap', 'bin')))

            """
            with chdir(self.lib_name):
                self.run('chmod +x configure')
                self.run('./configure --help')
                env_build = AutoToolsBuildEnvironment(self)
                self.run('autoreconf -f -i')  # Fix out of date aclocal
                env_build.configure(args=['--prefix', self.package_folder], build=False)
                env_build.make()
                env_build.make(args=['install'])
            """

    def package(self):
        if self.settings.os == "Windows":
            output_path = os.path.join(self.build_folder, self.lib_name, "gsoap", "VisualStudio2005")
            self.copy("*.exe", dst="bin", src=os.path.join(output_path, "soapcpp2", str(self.settings.build_type)))
            self.copy("*.exe", dst="bin", src=os.path.join(output_path, "wsdl2h", str(self.settings.build_type)))
        else:
            output_path = os.path.join(self.build_folder, self.lib_name, "gsoap", "bin")
            self.copy("soapcpp2", dst="bin", src=output_path)
            self.copy("wsdl2h", dst="bin", src=output_path)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
