#TODO MAKE THIS GENERIC
set (PYTHON_VERSION 3.8)

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

add_subdirectory(opentera/messages/python)

# Generate protobuf python files

set (translation_pot_file ${CMAKE_CURRENT_BINARY_DIR}/translations.pot)

message(STATUS "PYBABEL EXECUTABLE : ${PYBABEL_EXECUTABLE}")

# Will always be considered out of date...
add_custom_target(
    python-translations
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
add_custom_target(
    python-translations-compile-only
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    # TO REINITIALIZE TRANSLATION FILES (comment the two lines, or the translations will be overwritten)
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -l fr
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -l en
    # COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations
    DEPENDS python-env ${PYBABEL_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES babel.cfg
)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/opentera/OpenTeraServerVersion.py.in ${CMAKE_CURRENT_SOURCE_DIR}/opentera/OpenTeraServerVersion.py)

# Generate version file
add_custom_target(python-server-version SOURCES opentera/OpenTeraServerVersion.py.in)

# Will always be considered out of date...
add_custom_target(python-all DEPENDS python-env python-messages python-server-version python-translations-compile-only opentera/OpenTeraServerVersion.py)

# Build this target if you want to update translations too...
add_custom_target(python-all-with-translations DEPENDS python-all python-translations)

# Docker
add_subdirectory(docker)

# Services
add_subdirectory(services)
