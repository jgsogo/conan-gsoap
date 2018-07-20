
# Generate requested libraries:
#   - gsoap
#   - gsoap++
#   - gsoap_ssl
#   - gsoap_ssl++


set(OUTPUT_SUFFIX "")
if(${WITH_OPENSSL})
    set(OUTPUT_SUFFIX "ssl")
endif()


# C library
set(SRCS_GSOAP_C
    ${GSOAP_PATH}/gsoap/stdsoap2.c
    ${GSOAP_PATH}/gsoap/dom.c
)
set_source_files_properties(${SRCS_GSOAP_C} PROPERTIES LANGUAGE C)
add_library(gsoap ${SRCS_GSOAP_C} ${GSOAP_PATH}/gsoap/stdsoap2.h)
set_target_properties(gsoap PROPERTIES
    COMPILE_PDB_OUTPUT_DIRECTORY bin
    PDB_OUTPUT_DIRECTORY bin
    PUBLIC_HEADER ${GSOAP_PATH}/gsoap/stdsoap2.h
    LINKER_LANGUAGE C
    OUTPUT_NAME gsoap${OUTPUT_SUFFIX}
    )
install(TARGETS gsoap
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            PUBLIC_HEADER DESTINATION include
            )


# CXX library
set(SRCS_GSOAP_CXX
    ${GSOAP_PATH}/gsoap/stdsoap2.cpp
    ${GSOAP_PATH}/gsoap/dom.cpp
)
set_source_files_properties(${SRCS_GSOAP_CXX} PROPERTIES LANGUAGE CXX)
add_library(gsoap++ ${SRCS_GSOAP_CXX} ${GSOAP_PATH}/gsoap/stdsoap2.h)
set_target_properties(gsoap++ PROPERTIES
    COMPILE_PDB_OUTPUT_DIRECTORY bin
    PDB_OUTPUT_DIRECTORY bin
    PUBLIC_HEADER ${GSOAP_PATH}/gsoap/stdsoap2.h
    LINKER_LANGUAGE CXX
    OUTPUT_NAME gsoap${OUTPUT_SUFFIX}++
    )
install(TARGETS gsoap++
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            PUBLIC_HEADER DESTINATION include
            )

# Add SSL if requested
if(${WITH_OPENSSL})
    target_compile_definitions(gsoap PRIVATE WITH_OPENSSL WITH_GZIP)
    set_target_properties(gsoap PROPERTIES OUTPUT_NAME gsoapssl)
    target_compile_definitions(gsoap++ PRIVATE WITH_OPENSSL WITH_GZIP)
    set_target_properties(gsoap++ PROPERTIES OUTPUT_NAME gsoapssl++)
endif()
