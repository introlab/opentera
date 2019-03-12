# Protobuf files
SET(protofiles
    sample.proto
)

# Output directory for python/protobuf files
set(PROTOBUF_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/python)
file(MAKE_DIRECTORY ${PROTOBUF_OUTPUT_PATH})

# Targets
set(protobuf_python_files)

foreach(file ${protofiles})
    message(STATUS "Processing ${file}")
    get_filename_component (name_without_extension ${file} NAME_WE)
    #Add target
    set(output_target ${name_without_extension}.proto.target)
    list(APPEND protobuf_python_files ${output_target})
    #Add command to generate target
    add_custom_target(${output_target}
        COMMAND ${PROTOC_EXECUTABLE} ${file} -I=${CMAKE_CURRENT_SOURCE_DIR} --python_out ${PROTOBUF_OUTPUT_PATH}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS ${file} python-env)
endforeach(file)

add_custom_target(python-messages DEPENDS python-env ${protobuf_python_files})
