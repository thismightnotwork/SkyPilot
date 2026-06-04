# Tests require Qt6::Test — add to root CMakeLists via add_subdirectory(tests)
cmake_minimum_required(VERSION 3.24)
find_package(Qt6 REQUIRED COMPONENTS Test)

function(skyhigh_add_test name src)
    add_executable(${name} ${src})
    target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR}/src)
    target_link_libraries(${name} PRIVATE Qt6::Test Qt6::Core)
    add_test(NAME ${name} COMMAND ${name})
endfunction()

skyhigh_add_test(test_fsd_parser   test_fsd_parser.cpp)
skyhigh_add_test(test_fsd_protocol test_fsd_protocol.cpp)
