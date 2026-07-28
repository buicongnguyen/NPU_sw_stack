cmake_minimum_required(VERSION 3.20)

project(
  npu_sw_stack
  VERSION 0.1.0
  LANGUAGES CXX
)

include(CTest)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(NPU_ENABLE_SANITIZERS "Enable address and undefined-behavior sanitizers" OFF)

add_library(
  npu_model
  STATIC
  src/numerics.cpp
)

target_include_directories(
  npu_model
  PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_options(
  npu_model
  PRIVATE
  $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall;-Wextra;-Wpedantic;-Wconversion;-Wsign-conversion>
  $<$<CXX_COMPILER_ID:MSVC>:/W4;/permissive->
)

if(NPU_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(npu_model PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
  target_link_options(npu_model PUBLIC -fsanitize=address,undefined)
endif()

if(BUILD_TESTING)
  add_executable(test_numerics_cpp tests/cpp/test_numerics.cpp)
  target_link_libraries(test_numerics_cpp PRIVATE npu_model)
  target_compile_definitions(
    test_numerics_cpp
    PRIVATE
    NPU_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
  )
  add_test(NAME numerics_cpp COMMAND test_numerics_cpp)
endif()
