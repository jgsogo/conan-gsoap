
# Find gSOAP installed (by this Conan recipe)
#
# This code sets the following variables:
#
#   - GSOAP_IMPORT_DIR      = full path to the gsoap import directory
#   - GSOAP_LIBRARIES       = full path to the gsoap libraries
#   - GSOAP_SSL_LIBRARIES   = full path to the gsoap ssl libraries
#   - GSOAP_INCLUDE_DIR     = include dir to be used when using the gsoap library
#   - GSOAP_WSDL2H          = wsdl2h binary
#   - GSOAP_SOAPCPP2        = soapcpp2 binary
#   - GSOAP_FOUND           = set to true if gsoap was found successfully
#
#   - GSOAP_ROOT
#       setting this enables search for gsoap libraries / headers in this location
#
# Macros:
#
# GSOAP_TARGET(gsoap_input gsoap_output)
#
#   - Calls wsdl2h and soapcpp2
#     In case you specify a .wsdl file for "gsoap_input" wsdl2h is called first
#     then its output is passed to soapcpp2. Otherwise (in case of a header file)
#     only soapcpp2 is called. Namespace and servicename are parsed from the headerfile
#     which is given to soapcpp2.
#
#   Variables defined by this macro:
#     ${gsoap_output}_STUBS   contains the gsoap stubs
#     ${gsoap_output}_CLIENT  conatins the client sources
#     ${gsoap_output}_SERVER  contains the server sources
#     ${gsoap_output}_HEADER  contains the header passed to soapcpp2
#
#
# Credit: https://github.com/nherbaut/cmake-gsoap-simple-example/blob/master/src/cmake/Modules/FindGSOAP.cmake (for find itself)
# Credit: https://github.com/hlrs-vis/covise/blob/master/cmake/FindGSOAP.cmake (for macros)

set(GSOAP_ROOT ${CONAN_GSOAP_ROOT} CACHE PATH "Path to gSOAP installed by Conan")

# -----------------------------------------------------
# GSOAP Import Directories
# -----------------------------------------------------
find_path(GSOAP_IMPORT_DIR
  NAMES wsa.h
  PATHS ${GSOAP_ROOT}/import
)

# -----------------------------------------------------
# GSOAP Libraries
# -----------------------------------------------------
# find_library(GSOAP_CXX_LIBRARIES
	# NAMES gsoap++
	# HINTS ${GSOAP_ROOT}/lib ${GSOAP_ROOT}/lib64
		  # ${GSOAP_ROOT}/lib32
	# DOC "The main gsoap library"
# )
# find_library(GSOAP_SSL_CXX_LIBRARIES
	# NAMES gsoapssl++
	# HINTS ${GSOAP_ROOT}/lib ${GSOAP_ROOT}/lib64
		  # ${GSOAP_ROOT}/lib32
	# DOC "The ssl gsoap library"
# )

# find_library(GSOAP_C_LIBRARIES
	# NAMES gsoap
	# HINTS ${GSOAP_ROOT}/lib ${GSOAP_ROOT}/lib64
		  # ${GSOAP_ROOT}/lib32
	# DOC "The main gsoap library"
# )
# find_library(GSOAP_SSL_C_LIBRARIES
	# NAMES gsoapssl
	# HINTS ${GSOAP_ROOT}/lib ${GSOAP_ROOT}/lib64
		  # ${GSOAP_ROOT}/lib32
	# DOC "The ssl gsoap library"
# )

# -----------------------------------------------------
# GSOAP Include Directories
# -----------------------------------------------------
find_path(GSOAP_INCLUDE_DIR
	NAMES stdsoap2.h
	HINTS ${GSOAP_ROOT} ${GSOAP_ROOT}/include ${GSOAP_ROOT}/include/*
	DOC "The gsoap include directory"
)

# -----------------------------------------------------
# GSOAP Sources (if gsoap++ library is not provided)
# -----------------------------------------------------
set(GSOAP_SOURCES ${GSOAP_INCLUDE_DIR}/stdsoap2.h ${GSOAP_ROOT}/src/stdsoap2.cpp)


# -----------------------------------------------------
# GSOAP Binaries
# ----------------------------------------------------
if(NOT GSOAP_TOOL_DIR)
	set(GSOAP_TOOL_DIR GSOAP_ROOT)
endif()

find_program(GSOAP_WSDL2H
	NAMES wsdl2h
	HINTS ${GSOAP_TOOL_DIR}/bin
	DOC "The gsoap 'wsdl2h' tool"
)
find_program(GSOAP_SOAPCPP2
	NAMES soapcpp2
	HINTS ${GSOAP_TOOL_DIR}/bin
	DOC "The gsoap 'soapcpp2' tool"
)

# -----------------------------------------------------
# GSOAP version: this project starts on 2.8.68, no compatiblity issues yet.
# ----------------------------------------------------
execute_process(COMMAND ${GSOAP_SOAPCPP2}  "-V"   OUTPUT_VARIABLE GSOAP_STRING_VERSION ERROR_VARIABLE GSOAP_STRING_VERSION )
string(REGEX MATCH "[0-9]*\\.[0-9]*\\.[0-9]*" GSOAP_VERSION ${GSOAP_STRING_VERSION})

# -----------------------------------------------------
# handle the QUIETLY and REQUIRED arguments and set GSOAP_FOUND to TRUE if
# all listed variables are TRUE
# -----------------------------------------------------
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(gsoap DEFAULT_MSG 
    # GSOAP_CXX_LIBRARIES
    # GSOAP_C_LIBRARIES
    # GSOAP_INCLUDE_DIR
    GSOAP_WSDL2H
    GSOAP_SOAPCPP2)
mark_as_advanced(GSOAP_WSDL2H GSOAP_SOAPCPP2 
                 #GSOAP_INCLUDE_DIR 
                 # GSOAP_LIBRARIES 
                 )
