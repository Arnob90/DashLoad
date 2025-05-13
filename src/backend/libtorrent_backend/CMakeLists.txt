# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(cpp_template)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(NOT APPLE)
	# set(CMAKE_CXX_CLANG_TIDY clang-tidy)
endif()

# Find dependencies provided by vcpkg (via vcpkg.cmake)
find_package(fmt CONFIG REQUIRED)

set(
				CPP_TEMPLATE_SOURCES
				src/main.cpp
				src/torrenting/TorrentDownloader.cpp
)
set(
				CPP_TEMPLATE_TEST_SOURCES
				src/test.cpp
)
include_directories(include)
find_package(LibtorrentRasterbar CONFIG REQUIRED)
# main target
add_executable(main ${CPP_TEMPLATE_SOURCES})
target_link_libraries(main PRIVATE LibtorrentRasterbar::torrent-rasterbar)
target_link_libraries(main PRIVATE fmt::fmt)
target_include_directories(main PRIVATE include)
set_property(TARGET main PROPERTY CXX_STANDARD 23)
find_package(asio CONFIG REQUIRED)
# tests target
add_executable(tests ${CPP_TEMPLATE_TEST_SOURCES})
target_link_libraries(tests PRIVATE fmt::fmt)
set_property(TARGET tests PROPERTY CXX_STANDARD 23)
enable_testing()
add_test(tests tests)

add_custom_target(
				check-format
				COMMAND clang-format --dry-run ${CPP_TEMPLATE_SOURCES} ${CPP_TEMPLATE_TEST_SOURCES}
				WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
				COMMENT "checking format in src..."
)

add_custom_target(
				format
				COMMAND clang-format -i ${CPP_TEMPLATE_SOURCES} ${CPP_TEMPLATE_TEST_SOURCES}
				WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
				COMMENT "checking format in src..."
)
