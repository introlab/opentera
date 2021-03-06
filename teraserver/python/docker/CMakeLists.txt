# Automate docker setup here

# WORKDIR /opentera/teraserver/python
# Generate translations
# RUN pybabel extract -F babel.cfg -o translations.pot .
# RUN pybabel update -i translations.pot -d translations
# RUN pybabel compile -d translations

set(translation_pot_file translations.pot)
set(MESSAGES_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../messages)
set(PYBABEL_EXECUTABLE pybabel)
set(PROTOC_EXECUTABLE protoc)
set(GOOGLE_PROTO_PATH /usr/include/google/protobuf/)

# Will always be considered out of date...
add_custom_target(
    docker-translations
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../
)

FILE(GLOB_RECURSE protofiles RELATIVE "${MESSAGES_PATH}" "${MESSAGES_PATH}/*.proto")
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
    # message(STATUS "Should run: ${PROTOC_EXECUTABLE} ${file} -I. -I${GOOGLE_PROTO_PATH} --python_out ${MESSAGES_PATH}/python")
    add_custom_target(${output_target}
        COMMAND ${PROTOC_EXECUTABLE} ${file} -I. -I${GOOGLE_PROTO_PATH} --python_out ${MESSAGES_PATH}/python
        WORKING_DIRECTORY ${MESSAGES_PATH}
        DEPENDS ${MESSAGES_PATH}/${file} )
endforeach(file)

add_custom_target(
    docker-messages
    DEPENDS ${docker_protobuf_python_targets}
    WORKING_DIRECTORY ${MESSAGES_PATH}
)


add_custom_target(docker-all
    DEPENDS docker-translations docker-messages
)
