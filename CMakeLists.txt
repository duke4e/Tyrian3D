cmake_minimum_required(VERSION 3.21)
project(Tyrian3D C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE RelWithDebInfo)
endif()

find_package(SDL3 REQUIRED CONFIG)
# Homebrew's assimp CMake package hard-codes an SDK path for zlib, so link the library directly.
find_path(ASSIMP_INCLUDE_DIR assimp/cimport.h REQUIRED)
find_library(ASSIMP_LIBRARY assimp REQUIRED)
find_package(ZLIB REQUIRED)

set(BTBH_DIR "${CMAKE_SOURCE_DIR}/external/btbh-renderer")

# --- BTBH renderer: SDL_GPU backend (Metal on macOS, Vulkan elsewhere) -------------------------

file(GLOB BTBH_GPU_SOURCES CONFIGURE_DEPENDS "${BTBH_DIR}/src/gpu/*.c")
add_library(btbh_gpu STATIC ${BTBH_GPU_SOURCES})
target_include_directories(btbh_gpu
    PUBLIC "${BTBH_DIR}/include"
    PRIVATE "${BTBH_DIR}/external/raylib/src/external" "${ASSIMP_INCLUDE_DIR}"
)
target_compile_definitions(btbh_gpu PRIVATE SDL_MAIN_HANDLED BTBH_GPU_HAS_ASSIMP=1)
target_link_libraries(btbh_gpu PRIVATE SDL3::SDL3 "${ASSIMP_LIBRARY}" ZLIB::ZLIB)

# --- Shaders: HLSL -> SPIR-V (Vulkan) or -> MSL -> metallib (Metal) via SDL_shadercross --------

find_program(SHADERCROSS shadercross
    HINTS "${CMAKE_SOURCE_DIR}/build/shadercross"
    REQUIRED
)

set(TYR3D_SHADER_DIR "${CMAKE_BINARY_DIR}/shaders")
file(MAKE_DIRECTORY "${TYR3D_SHADER_DIR}")

# Take the production shader list straight from the renderer so the two stay in sync.
file(STRINGS "${BTBH_DIR}/CMakeLists.txt" BTBH_SHADER_SPEC_LINES
    REGEX "\"production_[a-z0-9_]+\\.(vert|frag|comp)\\|(vertex|fragment|compute)\"")

set(TYR3D_SHADER_OUTPUTS)
foreach(line IN LISTS BTBH_SHADER_SPEC_LINES)
    string(REGEX MATCH "production_[a-z0-9_]+\\.(vert|frag|comp)\\|(vertex|fragment|compute)" spec "${line}")
    string(REPLACE "|" ";" parts "${spec}")
    list(GET parts 0 name)
    list(GET parts 1 stage)
    set(src "${BTBH_DIR}/shaders/gpu_spike/${name}.hlsl")
    set(spv "${TYR3D_SHADER_DIR}/${name}.spv")
    add_custom_command(
        OUTPUT "${spv}"
        COMMAND "${SHADERCROSS}" "${src}" -s HLSL -d SPIRV -t ${stage} -e main
                -I "${BTBH_DIR}/shaders/gpu_spike" -o "${spv}"
        DEPENDS "${src}"
        IMPLICIT_DEPENDS C "${src}"
        COMMENT "shadercross ${name} -> SPIR-V"
        VERBATIM
    )
    if(APPLE)
        set(msl "${TYR3D_SHADER_DIR}/${name}.msl")
        set(air "${TYR3D_SHADER_DIR}/${name}.air")
        set(metallib "${TYR3D_SHADER_DIR}/${name}.metallib")
        add_custom_command(
            OUTPUT "${metallib}"
            COMMAND "${SHADERCROSS}" "${spv}" -s SPIRV -d MSL -t ${stage} -e main
                    --msl-version 2.4.0 -o "${msl}"
            COMMAND xcrun -sdk macosx metal -std=macos-metal2.4 -x metal -c "${msl}" -o "${air}"
            COMMAND xcrun -sdk macosx metallib "${air}" -o "${metallib}"
            DEPENDS "${spv}"
            COMMENT "metal ${name}"
            VERBATIM
        )
        list(APPEND TYR3D_SHADER_OUTPUTS "${metallib}")
    else()
        list(APPEND TYR3D_SHADER_OUTPUTS "${spv}")
    endif()
endforeach()

foreach(asset brdf_lut_512_rg16_float.raw smaa_area_160x560_rg8.raw smaa_search_64x16_r8.raw)
    add_custom_command(
        OUTPUT "${TYR3D_SHADER_DIR}/${asset}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BTBH_DIR}/assets/${asset}" "${TYR3D_SHADER_DIR}/${asset}"
        DEPENDS "${BTBH_DIR}/assets/${asset}"
        VERBATIM
    )
    list(APPEND TYR3D_SHADER_OUTPUTS "${TYR3D_SHADER_DIR}/${asset}")
endforeach()

add_custom_target(tyrian3d_shaders DEPENDS ${TYR3D_SHADER_OUTPUTS})

# --- Game ---------------------------------------------------------------------------------------

file(GLOB TYRIAN_SOURCES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/src/*.c")

add_executable(tyrian3d ${TYRIAN_SOURCES})
add_dependencies(tyrian3d tyrian3d_shaders)
target_link_libraries(tyrian3d PRIVATE btbh_gpu SDL3::SDL3 ZLIB::ZLIB m)
# cgltf (compiled into btbh_gpu) reads the models' material names.
target_include_directories(tyrian3d PRIVATE "${BTBH_DIR}/external/raylib/src/external")
# Upstream OpenTyrian always builds with NDEBUG; some of its asserts fire on valid Tyrian 2000 data.
target_compile_definitions(tyrian3d PRIVATE
    NDEBUG
    TYRIAN_DIR="${CMAKE_SOURCE_DIR}/data/tyrian2000"
    TYR3D_SHADER_DIR="${TYR3D_SHADER_DIR}"
    TYR3D_MODEL_DIR="${CMAKE_SOURCE_DIR}/assets/models"
    TYR3D_SIDES_DIR="${CMAKE_SOURCE_DIR}/assets/sides"
)
target_compile_options(tyrian3d PRIVATE
    -Wall -Wextra -Wno-missing-field-initializers -Wno-sign-compare -Wno-unused-parameter
)
