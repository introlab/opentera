find_package(Qt5Core REQUIRED)
find_package(Qt5WebEngine REQUIRED)
find_package(Qt5WebEngineWidgets REQUIRED)
find_package(Qt5Multimedia  REQUIRED)

set(headers
    ClientApp.h
    ConfigManagerClient.h
    LoginDialog.h
    ComManager.h
    MainWindow.h
    NotificationWindow.h
    Message.h
    GlobalMessageBox.h
    editors/DataEditorWidget.h
    editors/UserWidget.h
    editors/TeraForm.h
)

set(srcs
    main.cpp
    ClientApp.cpp
    ConfigManagerClient.cpp
    LoginDialog.cpp
    ComManager.cpp
    MainWindow.cpp
    NotificationWindow.cpp
    Message.cpp
    GlobalMessageBox.cpp
    editors/DataEditorWidget.cpp
    editors/UserWidget.cpp
    editors/TeraForm.cpp
)

SET(uis
    LoginDialog.ui
    MainWindow.ui
    notification.ui
    editors/UserWidget.ui
    editors/TeraForm.ui
)

SET(qrcs
    ${TERACLIENT_RES_INCLUDES}/TeraClient.qrc
)

#Generate .h files from the .ui files
QT5_WRAP_UI(moc_uis ${uis})

# generate rules for building source files from the resources
QT5_ADD_RESOURCES(client_qrc ${qrcs})

#This will generate moc_* for Qt
qt5_wrap_cpp(moc_srcs ${headers})

include_directories(
    ${TERACLIENT_RES_INCLUDES}
    ${OPENTERA_MESSAGES_INCLUDES}
    ${OPENTERA_SHARED_INCLUDES}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/editors
    ${CMAKE_CURRENT_BINARY_DIR})

# create an executable file named "TeraClient" from the source files
add_executable(TeraClient ${srcs} ${headers} ${moc_srcs} ${client_qrc} ${moc_uis})
qt5_use_modules(TeraClient Core Network Multimedia WebSockets WebEngine WebEngineWidgets WebSockets)

# Linking with Qt libraries and others
target_link_libraries(TeraClient ${OPENTERA_SHARED_LIBS})
set_target_properties(TeraClient PROPERTIES
        INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/bin
        INSTALL_RPATH_USE_LINK_PATH TRUE)

# Install target
install(TARGETS TeraClient DESTINATION bin)
