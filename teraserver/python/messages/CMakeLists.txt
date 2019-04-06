# Protobuf files
#SET(protofiles
#    sample.proto
#)

FILE(GLOB_RECURSE protofiles RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/*.proto")

message(STATUS "Protofiles: ${protofiles}")

# Include path
if(WIN32)
    set(GOOGLE_PROTO_PATH ${PYTHON_ENV_DIRECTORY}/Library/include/google/protobuf/)
else(WIN32)
    set(GOOGLE_PROTO_PATH ${PYTHON_ENV_DIRECTORY}/include/google/protobuf/)
endif(WIN32)


# Output directory for python/protobuf files
set(PROTOBUF_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/python)
file(MAKE_DIRECTORY ${PROTOBUF_OUTPUT_PATH})

# Targets
set(protobuf_python_targets)

foreach(file ${protofiles})
    message(STATUS "Processing ${file}")
    get_filename_component (name_without_extension ${file} NAME_WE)
    #Add target
    set(output_target ${name_without_extension}.proto.target)
    list(APPEND protobuf_python_targets ${output_target})
    #Add command to generate target
    add_custom_target(${output_target}
        COMMAND ${PROTOC_EXECUTABLE} ${file} -I=${CMAKE_CURRENT_SOURCE_DIR} -I${GOOGLE_PROTO_PATH} --python_out ${PROTOBUF_OUTPUT_PATH}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python-env ${file} )
endforeach(file)

add_custom_target(python-messages DEPENDS python-env ${protobuf_python_targets})
