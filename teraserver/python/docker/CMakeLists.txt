# Automate docker setup here
add_custom_target(docker-Dockerfile
    SOURCES Dockerfile
)

# WORKDIR /opentera/teraserver/python
# Generate translations
# RUN pybabel extract -F babel.cfg -o translations.pot .
# RUN pybabel update -i translations.pot -d translations
# RUN pybabel compile -d translations

set(translation_pot_file translations.pot)
set(MESSAGES_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../messages)
set(PYBABEL_EXECUTABLE pybabel)
set(PROTOC_EXECUTABLE protoc)
set(GOOGLE_PROTO_PATH /usr/python/Library/include/google/protobuf/)

# Will always be considered out of date...
add_custom_target(
    docker-translations
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations
    DEPENDS ${PYBABEL_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../

)

FILE(GLOB_RECURSE protofiles RELATIVE "${MESSAGES_PATH}" "${MESSAGES_PATH}/*.proto")
message(STATUS "Protofiles: ${protofiles}")

# Targets
set(docker_protobuf_python_targets)

foreach(file ${protofiles})
    message(STATUS "Processing ${file}")
    get_filename_component (name_without_extension ${file} NAME_WE)
    #Add target
    set(output_target docker_${name_without_extension}.proto.target)
    list(APPEND docker_protobuf_python_targets ${output_target})
    #Add command to generate target
    add_custom_target(${output_target}
        COMMAND ${PROTOC_EXECUTABLE} ${file} -I=${MESSAGES_PATH} -I${GOOGLE_PROTO_PATH} --python_out ${MESSAGES_PATH}/python
        WORKING_DIRECTORY ${MESSAGES_PATH}
        DEPENDS ${MESSAGES_PATH}/${file} )
endforeach(file)

add_custom_target(
    docker-messages
    DEPENDS ${PROTOC_EXECUTABLE} ${docker_protobuf_python_targets}
    WORKING_DIRECTORY ${MESSAGES_PATH}
)


add_custom_target(docker-all
    DEPENDS docker-Dockerfile docker-translations docker-messages
)
