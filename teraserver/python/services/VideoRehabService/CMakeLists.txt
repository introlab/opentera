set (translation_pot_file ${CMAKE_CURRENT_BINARY_DIR}/videorehabservice_translations.pot)

message(STATUS "PYBABEL EXECUTABLE : ${PYBABEL_EXECUTABLE}")

# Will always be considered out of date...
add_custom_target(
    videorehabservice-python-translations
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    # TO REINITIALIZE TRANSLATION FILES (comment the two lines, or the translations will be overwritten)
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -D videorehabservice -l fr
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -D videorehabservice -l en
    COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations -D videorehabservice
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations -D videorehabservice
    DEPENDS python-env ${PYBABEL_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/babel.cfg
)

# Will always be considered out of date...
add_custom_target(
    videorehabservice-python-translations-compile-only
    COMMAND ${PYBABEL_EXECUTABLE} extract -F babel.cfg -o ${translation_pot_file} .
    # TO REINITIALIZE TRANSLATION FILES (comment the two lines, or the translations will be overwritten)
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -D videorehabservice -l fr
    # COMMAND ${PYBABEL_EXECUTABLE} init -i ${translation_pot_file} -d translations -D videorehabservice -l en
    # COMMAND ${PYBABEL_EXECUTABLE} update -i ${translation_pot_file} -d translations -D videorehabservice
    COMMAND ${PYBABEL_EXECUTABLE} compile -d translations -D videorehabservice
    DEPENDS python-env ${PYBABEL_EXECUTABLE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/babel.cfg
)


# Build this target if you want to update translations too...
add_custom_target(videorehabservice-python-all-with-translations DEPENDS python-translations videorehabservice-python-translations)

# Build this target if you want to compile translations only
add_custom_target(videorehabservice-python-all-with-translations-compile-only DEPENDS python-translations-compile-only videorehabservice-python-translations-compile-only)
