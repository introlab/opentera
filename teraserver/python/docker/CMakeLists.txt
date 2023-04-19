set(MESSAGES_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../opentera/messages)
set(PYBABEL_EXECUTABLE pybabel)
set(PROTOC_EXECUTABLE protoc)
set(GOOGLE_PROTO_PATH /usr/include/google/protobuf/)


# Install python packages.
add_custom_target(
    docker-python-packages-install
    COMMAND python3 -m pip install -r requirements.txt protobuf==3.20.3 debugpy
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../env
)

# Generate translations for teraserver
add_custom_target(
    docker-translations-teraserver
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../
)

# Generate translations for logging service
add_custom_target(
    docker-translations-logging-service
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations -D loggingservice
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../services/LoggingService
)

# Generate translations for filetransfer service
add_custom_target(
    docker-translations-filetransfer-service
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations -D filetransferservice
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../services/FileTransferService
)

# Generate translations for videorehab service
add_custom_target(
    docker-translations-videorehab-service
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations -D videorehabservice
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../services/VideoRehabService
)

add_custom_target(
    docker-translations
    DEPENDS docker-translations-teraserver 
    DEPENDS docker-translations-logging-service 
    DEPENDS docker-translations-filetransfer-service
    DEPENDS docker-translations-videorehab-service
)

FILE(GLOB_RECURSE protofiles RELATIVE "${MESSAGES_PATH}" "${MESSAGES_PATH}/proto/*.proto")
message(STATUS "Docker Protofiles: ${protofiles}")
message(STATUS "Docker Message path: ${MESSAGES_PATH}")

# Targets
set(docker_protobuf_python_targets)

foreach(file ${protofiles})
    message(STATUS "Docker Processing ${file}")
    get_filename_component (name_without_extension ${file} NAME_WE)
    message(STATUS "Docker name_without_extension = ${name_without_extension}")
    #Add target
    set(output_target docker_${name_without_extension}.proto.target)
    list(APPEND docker_protobuf_python_targets ${output_target})
    #Add command to generate target
    add_custom_target(${output_target}
        COMMAND ${PROTOC_EXECUTABLE} ${file} -I./proto -I${GOOGLE_PROTO_PATH} --python_out ${MESSAGES_PATH}/python
        WORKING_DIRECTORY ${MESSAGES_PATH}
        DEPENDS ${MESSAGES_PATH}/${file} )
endforeach(file)

add_custom_target(
    docker-messages
    DEPENDS ${docker_protobuf_python_targets}
    WORKING_DIRECTORY ${MESSAGES_PATH}
)

add_custom_target(docker-python-all
    DEPENDS docker-python-packages-install docker-translations docker-messages
)
