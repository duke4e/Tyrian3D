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

# --- Episode 6 ------------------------------------------------------------------------------------
# Made from the game's data, so not in the repository: written to assets/content/episode6 when the
# data is there (tools/content/episode6/build.py).

find_package(Python3 COMPONENTS Interpreter)
set(TYR3D_EPISODE6_DIR "${CMAKE_SOURCE_DIR}/assets/content/episode6")
if(Python3_FOUND AND EXISTS "${CMAKE_SOURCE_DIR}/data/tyrian2000/tyrian5.lvl")
    file(GLOB TYR3D_EPISODE6_SOURCES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tools/content/episode6/*.py"
         "${CMAKE_SOURCE_DIR}/tools/content/episode6/levels/*.json")
    add_custom_command(
        OUTPUT "${TYR3D_EPISODE6_DIR}/tyrian6.lvl" "${TYR3D_EPISODE6_DIR}/levels6.dat" "${TYR3D_EPISODE6_DIR}/cubetxt6.dat"
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/content/episode6/build.py"
        DEPENDS ${TYR3D_EPISODE6_SOURCES} "${CMAKE_SOURCE_DIR}/tools/content/tyrformat.py"
                "${CMAKE_SOURCE_DIR}/tools/content/tyrdata.py" "${CMAKE_SOURCE_DIR}/tools/content/tyrevents.py"
        COMMENT "episode 6"
        VERBATIM
    )
    add_custom_target(tyrian3d_episode6 DEPENDS "${TYR3D_EPISODE6_DIR}/tyrian6.lvl")
endif()

# --- Episode 7 (the GBC levels) ---------------------------------------------------------------------
# Made from episode 7's levels (data/gbc/episode7, in the repository; tools/gbc/episode.py makes them from
# the GBC ROM): written to assets/content/episode7 when those levels are there (tools/content/gbc/build.py).

set(TYR3D_EPISODE7_DIR "${CMAKE_SOURCE_DIR}/assets/content/episode7")
if(Python3_FOUND AND EXISTS "${CMAKE_SOURCE_DIR}/data/gbc/episode7/episode.json")
    file(GLOB TYR3D_EPISODE7_SOURCES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tools/content/gbc/*.py"
         "${CMAKE_SOURCE_DIR}/data/gbc/episode7/levels/*.json")
    add_custom_command(
        OUTPUT "${TYR3D_EPISODE7_DIR}/tyrian7.lvl" "${TYR3D_EPISODE7_DIR}/levels7.dat" "${TYR3D_EPISODE7_DIR}/cubetxt7.dat"
               "${TYR3D_EPISODE7_DIR}/newshw.shp"
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/content/gbc/build.py"
        DEPENDS ${TYR3D_EPISODE7_SOURCES} "${CMAKE_SOURCE_DIR}/data/gbc/episode7/episode.json"
                "${CMAKE_SOURCE_DIR}/tools/content/gbc/new_enemies.json" "${CMAKE_SOURCE_DIR}/tools/content/gbc/newshw.shp"
                "${CMAKE_SOURCE_DIR}/data/gbc/shop.json"
                "${CMAKE_SOURCE_DIR}/tools/content/tyrformat.py" "${CMAKE_SOURCE_DIR}/tools/content/episode6/build.py"
                "${CMAKE_SOURCE_DIR}/tools/content/episode6/enemydata.py"
        COMMENT "episode 7"
        VERBATIM
    )
    add_custom_target(tyrian3d_episode7 DEPENDS "${TYR3D_EPISODE7_DIR}/tyrian7.lvl")
endif()

# --- Game ---------------------------------------------------------------------------------------

file(GLOB TYRIAN_SOURCES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/src/*.c")

add_executable(tyrian3d ${TYRIAN_SOURCES})
add_dependencies(tyrian3d tyrian3d_shaders)
if(TARGET tyrian3d_episode6)
    add_dependencies(tyrian3d tyrian3d_episode6)
endif()
if(TARGET tyrian3d_episode7)
    add_dependencies(tyrian3d tyrian3d_episode7)
endif()
target_link_libraries(tyrian3d PRIVATE btbh_gpu SDL3::SDL3 ZLIB::ZLIB m)
# cgltf (compiled into btbh_gpu) reads the models' material names.
target_include_directories(tyrian3d PRIVATE "${BTBH_DIR}/external/raylib/src/external")
# TinySoundFont (MIT, external/tinysoundfont) plays the music as MIDI (src/music_midi.c).
target_include_directories(tyrian3d PRIVATE "${CMAKE_SOURCE_DIR}/external/tinysoundfont")
# Upstream OpenTyrian always builds with NDEBUG; some of its asserts fire on valid Tyrian 2000 data.
target_compile_definitions(tyrian3d PRIVATE
    NDEBUG
    TYRIAN_DIR="${CMAKE_SOURCE_DIR}/data/tyrian2000"
    TYR3D_SHADER_DIR="${TYR3D_SHADER_DIR}"
    TYR3D_MODEL_DIR="${CMAKE_SOURCE_DIR}/assets/models"
    TYR3D_SIDES_DIR="${CMAKE_SOURCE_DIR}/assets/sides"
    TYR3D_TERRAIN_DIR="${CMAKE_SOURCE_DIR}/assets/terrain"
    TYR3D_FONT_DIR="${CMAKE_SOURCE_DIR}/assets/fonts"
    TYR3D_FEEDBACK_DIR="${CMAKE_SOURCE_DIR}/export/feedback"
    TYR3D_CONTENT_DIR="${CMAKE_SOURCE_DIR}/assets/content"
    TYR3D_CUSTOM_DIR="${CMAKE_SOURCE_DIR}/data/custom"
    TYR3D_SOUNDFONT_DIR="${CMAKE_SOURCE_DIR}/data/soundfonts"
    TYR3D_VOICES_DIR="${CMAKE_SOURCE_DIR}/data/voices"
    TYR3D_UPSCALE_DIR="${CMAKE_SOURCE_DIR}/data/hd"
)
target_compile_options(tyrian3d PRIVATE
    -Wall -Wextra -Wno-missing-field-initializers -Wno-sign-compare -Wno-unused-parameter
)
