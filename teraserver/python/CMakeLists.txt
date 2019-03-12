#TODO MAKE THIS GENERIC
set (PYTHON_VERSION 3.7)

# This will create environment from Anaconda
add_subdirectory(env)

set(PYTHON_ENV_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/env/python-${PYTHON_VERSION})

if(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python.exe)
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip.exe)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyinstaller.exe)
    set(PROTOC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Library/bin/protoc.exe)
else(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python)
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pyinstaller)
    set(PROTOC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/protoc)
endif(WIN32)

add_subdirectory(messages)

# Generate protobuf python files

add_custom_target(python-all DEPENDS python-messages python-env)

