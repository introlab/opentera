project(OpenTeraServer)
cmake_minimum_required(VERSION 3.5)

# Compile in debug or release mode
if(NOT CMAKE_BUILD_TYPE)
  #SET(CMAKE_BUILD_TYPE Release)
  set(CMAKE_BUILD_TYPE Debug)
endif(NOT CMAKE_BUILD_TYPE)

# Software version
SET(OPENTERA_VERSION_MAJOR "1")
SET(OPENTERA_VERSION_MINOR "0")
SET(OPENTERA_VERSION_PATCH "9")
SET(OPENTERA_SERVER_VERSION OpenTera_v${OPENTERA_VERSION_MAJOR}.${OPENTERA_VERSION_MINOR}.${OPENTERA_VERSION_PATCH})

MESSAGE("OpenTera Server Version : ${OPENTERA_SERVER_VERSION}")

# Main http server
add_subdirectory(python)

# Easyrtc process
add_subdirectory(easyrtc)

