#TODO MAKE THIS GENERIC
set (PYTHON_VERSION 3.6)

# This will create environment from Anaconda
add_subdirectory(env)

set(PYTHON_ENV_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/env/python-${PYTHON_VERSION})

if(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python.exe)
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip.exe)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyinstaller.exe)
    set(PROTOC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Library/bin/protoc.exe)
    set(PYBABEL_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pybabel.exe)
else(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python)
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pyinstaller)
    set(PROTOC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/protoc)
    set(PYBABEL_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pybabel)
endif(WIN32)

add_subdirectory(messages)

# Generate protobuf python files

set (translation_pot_file ${CMAKE_CURRENT_BINARY_DIR}/translations.pot)

message(STATUS "PYBABEL EXECUTABLE : ${PYBABEL_EXECUTABLE}")

# Will always be considered out of date...
add_custom_target(
    python_translations
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    # TO REINITIALIZE TRANSLATION FILES (comment the two lines, or the translations will be overwritten)
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -l fr
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -l en
    COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations
    DEPENDS python-env ${PYBABEL_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES babel.cfg
)


# Will always be considered out of date...
# Removed python-messages for now...
add_custom_target(python-all DEPENDS  python-env python_translations python-messages)

# Docker
add_subdirectory(docker)
