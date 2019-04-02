message(STATUS "Building easyrtc")

# find_package (Node REQUIRED)

if(WIN32)
    set(NPM_EXECUTABLE npm.exe)
else(WIN32)
    set(NPM_EXECUTABLE /usr/local/bin/npm)
endif(WIN32)

# Will always be considered out of date...
add_custom_target(
    easyrtc_install
    COMMAND ${NPM_EXECUTABLE} install
    DEPENDS ${NPM_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES package.json
)
