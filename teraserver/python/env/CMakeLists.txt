# Will try to install env if not present.
# Conda needs to be installed first



set (ENV_PATH ${CMAKE_CURRENT_SOURCE_DIR}/python-${PYTHON_VERSION})
file(MAKE_DIRECTORY ${ENV_PATH})

if(WIN32)
    message(STATUS "env $ENV{HOMEPATH}")
    set(CONDA_PATH "$ENV{SYSTEMDRIVE}$ENV{HOMEPATH}/Miniconda3/Scripts/conda.exe")
    set(PYTHON_PATH ${ENV_PATH}/python.exe)
else(WIN32)
    set(CONDA_PATH "$ENV{HOME}/miniconda3/bin/conda")
    set(PYTHON_PATH ${ENV_PATH}/bin/python)
endif(WIN32)

# Define packages to install
set (conda_packages
    protobuf
)

set (pip_packages
    twisted
    autobahn
    sqlalchemy
    psycopg2-binary
    python-oauth2
    flask
    flask-sqlalchemy
    flask-oauthlib
    flask-login
    flask-httpauth
    flask-socketio
    flask-session
    flask-restful
    flask-security
    flask-babel
    flask-migrate
    # flask-jwt
    redis
    txredisapi
    eventlet
    gevent
    gevent-websocket
    passlib
    bcrypt
    wtforms
    PyInstaller
    pyopenssl
    service_identity
    jsonrpcclient
    # jwt
    PyJWT
)

# Create environment, will produce python executable
add_custom_command(
  OUTPUT ${PYTHON_PATH}
  COMMAND ${CONDA_PATH} install -m -c conda-forge -y -p ${ENV_PATH} python=${PYTHON_VERSION} ${conda_packages}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# Will always be considered out of date...
# Always proceed...
# TODO - INSTALL WITH CONDA ?
add_custom_target(
  python-env
  COMMAND ${PYTHON_PATH} -m pip install ${pip_packages}
  WORKING_DIRECTORY ${ENV_PATH}
  DEPENDS ${PYTHON_PATH}
)


    


