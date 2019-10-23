project(OpenTera)

include(CTest)
enable_testing()
#include(CheckFunctionExists)

#Look for minimum cmake version
cmake_minimum_required(VERSION 3.0.2)

#DEFINITIONS POLICY, NEW SINCE 3.0.2
cmake_policy(SET CMP0043 NEW)

# Software version
SET(CPACK_PACKAGE_VERSION_MAJOR "0")
SET(CPACK_PACKAGE_VERSION_MINOR "1")
SET(CPACK_PACKAGE_VERSION_PATCH "0")
SET(CPACK_PACKAGE_VERSION ${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH})
add_definitions(-DTERAPLUS_VERSION="${CPACK_PACKAGE_VERSION}" )

# Compile in debug or release mode
if(NOT CMAKE_BUILD_TYPE)
  #SET(CMAKE_BUILD_TYPE Release)
  set(CMAKE_BUILD_TYPE Debug)
endif(NOT CMAKE_BUILD_TYPE)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

message(STATUS "Using QMAKE: ${QT_QMAKE_EXECUTABLE}")

# This will enable to output everything in the bin directory for testing and debugging...
SET (EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
SET (LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

# Shared data
add_subdirectory(shared)

# Client
add_subdirectory(client)

# Package
add_subdirectory(package)

# Readme and other files
add_custom_target(readme SOURCES README.md)
