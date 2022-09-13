# Will try to install env if not present.
# Conda needs to be installed first



set (ENV_PATH ${CMAKE_CURRENT_SOURCE_DIR}/python-${PYTHON_VERSION})
file(MAKE_DIRECTORY ${ENV_PATH})

# Define packages to install
set (conda_packages
    protobuf # ==3.18.1
)

if(WIN32)
    message(STATUS "env $ENV{HOMEPATH}")
    set(CONDA_PATH "$ENV{SYSTEMDRIVE}$ENV{HOMEPATH}/Miniconda3/Scripts/conda.exe")
    set(PYTHON_PATH ${ENV_PATH}/python.exe)
else(WIN32)
    set(CONDA_PATH "$ENV{HOME}/miniconda3/bin/conda")
    set(PYTHON_PATH ${ENV_PATH}/bin/python)
endif(WIN32)



# Use the requirements file instead of listing all packages in CMake.
add_custom_target(
    python-requirements
    SOURCES requirements.txt
)

# Create environment, will produce python executable
add_custom_command(
  OUTPUT ${PYTHON_PATH}
  COMMAND ${CONDA_PATH} install -m -c conda-forge -y -p ${ENV_PATH} python=${PYTHON_VERSION} ${conda_packages}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)


# TODO - INSTALL WITH CONDA ?


# Will always be considered out of date...
# Always proceed...
add_custom_target(
  python-env
  COMMAND ${PYTHON_PATH} -m pip install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt --upgrade
  WORKING_DIRECTORY ${ENV_PATH}
  DEPENDS ${PYTHON_PATH} python-requirements
)


    


