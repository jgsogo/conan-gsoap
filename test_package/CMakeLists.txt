cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GSOAP REQUIRED)

add_executable(example example.cpp
    ${CMAKE_BINARY_DIR}/soapC.cpp
    ${CMAKE_BINARY_DIR}/soapcalcProxy.cpp)
target_include_directories(example PRIVATE ${CMAKE_BINARY_DIR} ${GSOAP_INCLUDE_DIR})
target_link_libraries(example gsoapssl++ ${CONAN_LIBS})
