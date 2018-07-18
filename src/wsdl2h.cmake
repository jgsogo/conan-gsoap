
# Generate project for wsdl2h

set(SRC_CPP
    ${GSOAP_PATH}/gsoap/wsdl/wsdlC.cpp
    ${GSOAP_PATH}/gsoap/wsdl/wsdl2h.cpp
    ${GSOAP_PATH}/gsoap/wsdl/wsdl.cpp
    ${GSOAP_PATH}/gsoap/wsdl/wadl.cpp
    ${GSOAP_PATH}/gsoap/wsdl/schema.cpp
    ${GSOAP_PATH}/gsoap/wsdl/soap.cpp
    ${GSOAP_PATH}/gsoap/wsdl/mime.cpp
    ${GSOAP_PATH}/gsoap/wsdl/wsp.cpp
    ${GSOAP_PATH}/gsoap/wsdl/bpel.cpp
    ${GSOAP_PATH}/gsoap/wsdl/types.cpp
    ${GSOAP_PATH}/gsoap/wsdl/service.cpp
    ${GSOAP_PATH}/gsoap/stdsoap2.cpp
    )

if(${WITH_SSL})
    list(APPEND SRC_CPP
         ${GSOAP_PATH}/gsoap/plugin/httpda.c
         ${GSOAP_PATH}/gsoap/plugin/smdevp.c
        )
endif()

add_executable(wsdl2h ${SRC_CPP})
