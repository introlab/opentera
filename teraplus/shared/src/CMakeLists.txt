find_package(Qt5Core REQUIRED)

add_definitions(-DSHAREDLIB_LIBRARY)
if (MSVC)
    add_definitions(-DOPENTERAMESSAGES_EXPORT=__declspec\(dllimport\))
    add_definitions(
      /wd4910 # Ignore export warnings (C4910) with MSVC
      /wd4661 # Ignore no suitable definition for explicit template (C4661)
      /wd4251 # Ignore needs to have dll-interface
    )
endif(MSVC)

set(sharedlib_headers
    SharedLib.h
    Logger.h
    ConfigManager.h
    data/TeraUser.h
    data/TeraUserGroup.h
    data/TeraData.h
    WebAPI.h
)

set(sharedlib_srcs
    Logger.cpp
    ConfigManager.cpp
    data/TeraUser.cpp
    data/TeraUserGroup.cpp
    data/TeraData.cpp
)

include_directories(
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${OPENTERA_MESSAGES_INCLUDES}
)

#This will generate moc_* for Qt
qt5_wrap_cpp(sharedlib_moc_srcs ${sharedlib_headers})

#compile library
add_library(opentera_shared SHARED ${sharedlib_headers} ${sharedlib_srcs} ${sharedlib_moc_srcs})
qt5_use_modules(opentera_shared Core Network)
set_target_properties(opentera_shared PROPERTIES
        INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/bin
        INSTALL_RPATH_USE_LINK_PATH TRUE)
target_link_libraries(opentera_shared ${OPENTERA_MESSAGES_LIBS})
if (MSVC)
target_compile_definitions(opentera_shared PUBLIC OPENTERAMESSAGES_EXPORT=__declspec\(dllimport\))
endif(MSVC)


# Install target
install(TARGETS opentera_shared DESTINATION bin)

set(OPENTERA_SHARED_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/data CACHE INTERNAL "doc string")
set(OPENTERA_SHARED_LIBS "opentera_shared" CACHE INTERNAL "doc string")


# add_subdirectory(tests)
