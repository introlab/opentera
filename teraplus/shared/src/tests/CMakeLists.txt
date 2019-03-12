remove_definitions(-DSHAREDLIB_LIBRARY)

enable_testing()

#includes for all tests
include_directories(
    ${OPENTERA_MESSAGES_INCLUDES}
    ${OPENTERA_REP_INCLUDES}
    ${OPENTERA_SHARED_INCLUDES}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
)

# test_TeraUser
set(test_TeraUser_headers test_TeraUser.h)
set(test_TeraUser_srcs test_TeraUser.cpp)
qt5_wrap_cpp(test_TeraUser_moc_srcs ${test_TeraUser_headers})

add_executable(test_TeraUser ${test_TeraUser_moc_srcs} ${test_TeraUser_headers} ${test_TeraUser_srcs})
qt5_use_modules(test_TeraUser Core Network Xml XmlPatterns RemoteObjects WebSockets Test)

# Linking with Qt libraries and others
target_link_libraries(test_TeraUser ${OPENTERA_SHARED_LIBS})
set_target_properties(test_TeraUser PROPERTIES
        INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/bin
        INSTALL_RPATH_USE_LINK_PATH TRUE)


add_test(NAME TeraUser WORKING_DIRECTORY ${EXECUTABLE_OUTPUT_PATH} COMMAND test_TeraUser )

