
cmake_minimum_required(VERSION 2.8)

project(gSOAP)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

message("Generate gSOAP from sources at ${GSOAP_PATH}")

# Tools
include(${CMAKE_CURRENT_SOURCE_DIR}/soapcpp2.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/wsdl2h.cmake)

# Libraries
include(${CMAKE_CURRENT_SOURCE_DIR}/gsoap.cmake)

install(FILES ${GSOAP_PATH}/gsoap/typemap.dat DESTINATION /)
install(DIRECTORY ${GSOAP_PATH}/gsoap/import DESTINATION /)
