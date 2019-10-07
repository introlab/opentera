find_package(Qt5Core REQUIRED)
message(STATUS "Entering package directory.")


include(InstallRequiredSystemLibraries)
get_target_property(_qt5_qmake_location Qt5::qmake IMPORTED_LOCATION)

execute_process(
    COMMAND "${_qt5_qmake_location}" -query QT_INSTALL_PREFIX
    RESULT_VARIABLE return_code
    OUTPUT_VARIABLE qt5_install_prefix
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Testing package ${_qt5_qmake_location} ${qt5_install_prefix}")

if (APPLE)
    add_custom_target(package
        COMMAND ${qt5_install_prefix}/bin/macdeployqt "$<TARGET_FILE_DIR:TeraClient>/../.." -always-overwrite
        COMMENT "Running macdeplotqt ..."
        DEPENDS TeraClient
    )

endif(APPLE)
