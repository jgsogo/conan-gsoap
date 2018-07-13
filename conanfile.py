

import os
import shutil
from lxml import etree

from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake, RunEnvironment, MSBuild
from conans.errors import NotFoundException


class GSoap(ConanFile):
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
    options = {"with_openssl": [True, False]}
    default_options = "with_openssl=True"
    generators = "cmake"
    short_paths = True

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

    def _patch_soapcpp2(self, vcxproj):
        # MSVC 2015
        props_file = os.path.join(self.deps_cpp_info["winflexbison"].rootpath, "bin", "custom_build_rules", "win_flex_bison_custom_build.props")
        targets_file = os.path.join(self.deps_cpp_info["winflexbison"].rootpath, "bin", "custom_build_rules", "win_flex_bison_custom_build.targets")
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionSettings">', '<ImportGroup Label="ExtensionSettings"><Import Project="{}" />'.format(props_file))
        tools.replace_in_file(vcxproj, '<ImportGroup Label="ExtensionTargets">', '<ImportGroup Label="ExtensionTargets"><Import Project="{}" />'.format(targets_file))
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_lex.l" />', '<Flex Include="soapcpp2_lex.l"><FileType>Document</FileType><OutputFile>lex.%(Filename).c</OutputFile></Flex>')
        tools.replace_in_file(vcxproj, '<None Include="soapcpp2_yacc.y" />', '<Bison Include="soapcpp2_yacc.y"><FileType>Document</FileType><OutputFile>%(Filename).tab.c</OutputFile></Bison>')

    def _patch_wsdl2h(self, vcxproj):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(vcxproj, parser=parser)
        root = tree.getroot()
        if self.options.with_openssl:
            for conf_tools in root.xpath("./Configurations/Configuration/Tool[@Name='VCCLCompilerTool']"):
                conf_tools.attrib['PreprocessorDefinitions'] = ';'.join(["WITH_OPENSSL", conf_tools.attrib['PreprocessorDefinitions']])
                include_dirs = [os.path.join(self.deps_cpp_info["OpenSSL"].rootpath, inc_dir) for inc_dir in self.deps_cpp_info["OpenSSL"].includedirs]
                conf_tools.attrib['AdditionalIncludeDirectories'] = ';'.join(include_dirs + 
                                                                             [r'"{}"'.format(os.path.dirname(vcxproj)), 
                                                                              r'"{}"'.format(os.path.join(os.path.dirname(vcxproj), '..', '..', '..', 'plugin')),
                                                                              conf_tools.attrib.get('AdditionalIncludeDirectories', '')])

            for link_tool in root.xpath("./Configurations/Configuration/Tool[@Name='VCLinkerTool']"):
                libraries = ["{}.lib".format(lib) for lib in self.deps_cpp_info["OpenSSL"].libs] + ["User32.lib", "GDI32.lib", "Advapi32.lib", "msvcrt{}.lib".format("" if str(self.settings.build_type)=="Release" else "d")]  # TODO: Those additional libraries, are they needed in conan-openssl?
                link_tool.attrib['AdditionalDependencies'] = ' '.join(libraries + [link_tool.attrib['AdditionalDependencies'],])
                library_dirs = [os.path.join(self.deps_cpp_info["OpenSSL"].rootpath, libdir) for libdir in self.deps_cpp_info["OpenSSL"].libdirs]
                link_tool.attrib['AdditionalLibraryDirectories'] = ';'.join(library_dirs + [link_tool.attrib.get('AdditionalLibraryDirectories', ''),])

            source_files = root.xpath("./Files/Filter[@Name='Source Files']")
            assert len(source_files) == 1
            etree.SubElement(source_files[0], "File").set("RelativePath", "../../../plugin/httpda.c")
            etree.SubElement(source_files[0], "File").set("RelativePath", "../../../plugin/smdevp.c")
            etree.SubElement(source_files[0], "File").set("RelativePath", "../../../plugin/threads.c")

        tree.write(vcxproj, pretty_print=True, xml_declaration=True)

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
                self._patch_soapcpp2(os.path.join(soapcpp2_dir, "soapcpp2", "soapcpp2.vcxproj"))
                out = msbuild.build(soapcpp2_sln, upgrade_project=False, platforms={'x86': 'Win32'})

            # Build wsdl2h.exe
            wsdl2h_dir = os.path.abspath(os.path.join(self.lib_name, "gsoap", "VisualStudio2005", "wsdl2h"))
            # - copy soapcpp2.exe to wsdl2h directory (we want to use what we have compiled)
            shutil.copy2(os.path.join(soapcpp2_dir, str(self.settings.build_type), "soapcpp2.exe"),
                         os.path.join(wsdl2h_dir, "wsdl2h"))
            # - compile it
            wsdl2h_sln = os.path.join(wsdl2h_dir, "wsdl2h.sln")
            msbuild = MSBuild(self)
            self._patch_wsdl2h(os.path.join(wsdl2h_dir, "wsdl2h", "wsdl2h.vcproj"))
            out = msbuild.build(wsdl2h_sln, platforms={'x86': 'Win32'})

        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(configure_dir=self.lib_name, args=['--prefix', self.package_folder, ], build=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        output_path = os.path.join(self.build_folder, self.lib_name, "gsoap", "VisualStudio2005")
        self.copy("*.exe", dst="bin", src=os.path.join(output_path, "soapcpp2", str(self.settings.build_type)))
        self.copy("*.exe", dst="bin", src=os.path.join(output_path, "wsdl2h", str(self.settings.build_type)))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
