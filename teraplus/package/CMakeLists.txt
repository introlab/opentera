find_package(Qt5Core REQUIRED)
message(STATUS "Entering package directory.")

set(CPACK_PACKAGE_NAME "OpenTeraClient")
set(CPACK_PACKAGE_FILE_NAME OpenTera_${CPACK_PACKAGE_VERSION}_setup)
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "OpenTera - Client - Installateur")
set(CPACK_PACKAGE_VENDOR "Regroupement INTER")
#set(CPACK_COMPONENTS_ALL openteraclient_installer)
set(CPACK_PACKAGE_EXECUTABLES "TeraClient" "OpenTeraClient")

# SB - Those are required if using QT Installer Framework
#set(CPACK_GENERATOR IFW)
#set(CPACK_IFW_VERBOSE ON)
#set(CPACK_IFW_PACKAGE_START_MENU_DIRECTORY INTER_OpenTeraClient)
#set(CPACK_IFW_PACKAGE_NAME "OpenTeraClient")
#set(CPACK_IFW_PACKAGE_MAINTENANCE_TOOL_NAME "Uninstaller")
#set(CPACK_IFW_TARGET_DIRECTORY "@ApplicationsDirX64@/INTER/OpenTeraClient")
#set(CPACK_IFW_PACKAGE_WIZARD_STYLE "Modern")
#set(CPACK_IFW_PACKAGE_START_MENU_DIRECTORY "INTER/OpenTeraClient")
#include(CPackIFW REQUIRED)

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

if (WIN32)

    # Create files for installation
    add_custom_target(client_package
        # Collect and copy required dependencies
        COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/deploy"
        COMMAND ${qt5_install_prefix}/bin/windeployqt "$<TARGET_FILE_DIR:TeraClient>/TeraClient.exe" --release --dir "$<TARGET_FILE_DIR:TeraClient>/deploy"
        # Copy executables to deploy directory
        COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE_DIR:TeraClient>/TeraClient.exe" "$<TARGET_FILE_DIR:TeraClient>/deploy/TeraClient.exe"
        COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE_DIR:TeraClient>/opentera_shared.dll" "$<TARGET_FILE_DIR:TeraClient>/deploy/opentera_shared.dll"
        # Copy default configs to deploy directory
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/defaults" "$<TARGET_FILE_DIR:TeraClient>/deploy"
    )

    # Uses NSIS packaging system on Windows
    # SET(CPACK_SOURCE_GENERATOR "NSIS")
    # dTODO: License file
    # SET(CPACK_RESOURCE_FILE_LICENSE "${PROJECT_SOURCE_DIR}/COPYING.txt")

    SET(CPACK_NSIS_INSTALL_ROOT "C:\\\\INTER")
    SET(CPACK_PACKAGE_INSTALL_DIRECTORY "OpenTeraClient")
    SET(CPACK_NSIS_PACKAGE_NAME "OpenTera - Client v${CPACK_PACKAGE_VERSION}")
    SET(CPACK_NSIS_MODIFY_PATH OFF)
    SET(CPACK_NSIS_EXECUTABLES_DIRECTORY .)

    SET(CPACK_NSIS_DEFINES "!define MUI_STARTMENUPAGE_DEFAULTFOLDER \\\"OpenTeraClient\\\"
                                    VIProductVersion ${CPACK_PACKAGE_VERSION}.0
                                    VIAddVersionKey ProductName \\\"${CPACK_PACKAGE_NAME}\\\"
                                    VIAddVersionKey FileDescription \\\"${CPACK_PACKAGE_DESCRIPTION_SUMMARY}\\\"
                                    VIAddVersionKey Comments \\\"Installateur de ${CPACK_PACKAGE_NAME}\\\"
                                    VIAddVersionKey CompanyName \\\"${CPACK_PACKAGE_VENDOR}\\\"
                                    VIAddVersionKey LegalCopyright \\\"${CPACK_PACKAGE_VENDOR}\\\"
                                    VIAddVersionKey InternalName \\\"${CPACK_PACKAGE_NAME} Installer\\\"
                                    VIAddVersionKey LegalTrademarks \\\"\\\"
                                    VIAddVersionKey OriginalFilename \\\"${CPACK_PACKAGE_FILE_NAME}.exe\\\"
                                    VIAddVersionKey FileVersion ${CPACK_PACKAGE_VERSION}
                                    VIAddVersionKey ProductVersion ${CPACK_PACKAGE_VERSION}")

   include(CPack REQUIRED)

#   cpack_add_component(
#       openteraclient_installer
#       DISPLAY_NAME "OpenTera - Client"
#       DESCRIPTION "Le logiciel client d'OpenTera"
#       REQUIRED
#   )

# SB - Used with Qt Installer Framework
#    cpack_ifw_configure_component(
#        openteraclient_installer
#        NAME opentera.client.installer
#        VERSION "${CPACK_PACKAGE_VERSION}" # Version of component
#        # LICENSES License ${qt_cpackifw_SOURCE_DIR}/LICENSE
#        DEFAULT TRUE
#    )



   # Run VC++ redistributable
   list(APPEND CPACK_NSIS_EXTRA_INSTALL_COMMANDS "ExecWait 'cmd /c $INSTDIR\\\\VC_redist.x64.exe /install /passive /norestart'")

   # Set files to install - everything in deploy folder
   install(
       DIRECTORY $<TARGET_FILE_DIR:TeraClient>/deploy/
       DESTINATION .
      # COMPONENT openteraclient_installer
   )

endif (WIN32)
