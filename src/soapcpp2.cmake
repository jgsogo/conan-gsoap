
# Generate project for soapcpp2 executable

set(STDCPP2_PATH ${GSOAP_PATH}/gsoap/src/)
# set(STDCPP2_PATH ${GSOAP_PATH}/gsoap/VisualStudio2005/soapcpp2/soapcpp2)

set(SRC_CPP
    ${STDCPP2_PATH}/symbol2.c
    ${STDCPP2_PATH}/error2.c
    ${STDCPP2_PATH}/init2.c
    ${STDCPP2_PATH}/soapcpp2.c
    ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
    #${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.h
    ${CMAKE_BINARY_DIR}/generated/lex.yy.c
    )
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.h PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/lex.yy.c PROPERTIES GENERATED TRUE)


if(WIN32)
    set(CMD_PREFIX "win_")
else()
    set(CMD_PREFIX "")
endif()

add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
    COMMAND ${CONAN_WINFLEXBISON_ROOT}/bin/${CMD_PREFIX}bison -d -v -o ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c ${STDCPP2_PATH}/soapcpp2_yacc.y
    COMMENT "Run BISON on soapcpp2"
    )

add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/generated/lex.yy.c
    COMMAND ${CONAN_WINFLEXBISON_ROOT}/bin/${CMD_PREFIX}flex --wincompat -o ${CMAKE_BINARY_DIR}/generated/lex.yy.c ${STDCPP2_PATH}/soapcpp2_lex.l
    COMMENT "Run FLEX on soapcpp2"
    )

add_custom_target(FLEXBISON_GENERATORS
    DEPENDS
        ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
        ${CMAKE_BINARY_DIR}/generated/lex.yy.c)


add_executable(soapcpp2 ${SRC_CPP})
target_include_directories(soapcpp2 PRIVATE ${STDCPP2_PATH})
set_source_files_properties(${SRC_CPP} PROPERTIES LANGUAGE C)
add_dependencies(soapcpp2 FLEXBISON_GENERATORS)
install(TARGETS soapcpp2 RUNTIME DESTINATION bin)
