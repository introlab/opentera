project(TeraServer)
cmake_minimum_required(VERSION 3.8)

# Compile in debug or release mode
if(NOT CMAKE_BUILD_TYPE)
  #SET(CMAKE_BUILD_TYPE Release)
  set(CMAKE_BUILD_TYPE Debug)
endif(NOT CMAKE_BUILD_TYPE)

add_subdirectory(cpp)

#Disabled for now.
#This is en experimental HTTP server
add_subdirectory(python)




