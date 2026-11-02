@echo off
rem Builds the game on Windows, as tools/bootstrap.sh does on macOS, with Visual Studio 2022 (the C++
rem workload: MSVC, its vcpkg, CMake and Ninja): SDL3 (with its Vulkan GPU backend), assimp and zlib from
rem vcpkg.json into build\vcpkg_installed, the shader compiler (SDL_shadercross with DXC, built once: long
rem the first time) and the game, in build\game\tyrian3d.exe. The data comes first, from Git Bash:
rem tools/fetch_data.sh. The clone wants LF line endings (git config core.autocrlf false before checkout:
rem with CRLF the shell scripts and the data's checksums fail).
rem usage: tools\build_windows.bat
setlocal
set "ROOT=%~dp0.."
for %%i in ("%ROOT%") do set "ROOT=%%~fi"
set "VS=%ProgramFiles%\Microsoft Visual Studio\2022\Community"
if not exist "%VS%\VC\Auxiliary\Build\vcvars64.bat" (echo Visual Studio 2022 Community is missing >&2 & exit /b 1)
call "%VS%\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "%ROOT%"
if not exist data\tyrian2000\tyrian.hdt (echo no Tyrian 2000 data: run tools/fetch_data.sh from Git Bash >&2 & exit /b 1)

rem (the game's configure installs vcpkg.json's libraries, which shadercross needs too; CMake on MSVC
rem defaults to Debug, so the build type is given)
cmake -G Ninja -S . -B build/game -DCMAKE_BUILD_TYPE=RelWithDebInfo ^
	-DCMAKE_TOOLCHAIN_FILE="%VS%/VC/vcpkg/scripts/buildsystems/vcpkg.cmake" ^
	-DVCPKG_TARGET_TRIPLET=x64-windows -DVCPKG_INSTALLED_DIR="%ROOT%/build/vcpkg_installed" ^
	-DSHADERCROSS="%ROOT%/build/shadercross/shadercross.exe" || exit /b 1

if not exist build\shadercross\shadercross.exe (
	git submodule update --init external/btbh-renderer || exit /b 1
	git -C external/btbh-renderer submodule update --init external/raylib || exit /b 1
	git -C external/btbh-renderer submodule update --init --recursive external/SDL_shadercross || exit /b 1
	cmake -G Ninja -S external/btbh-renderer/external/SDL_shadercross -B build/shadercross -DCMAKE_BUILD_TYPE=Release ^
		-DCMAKE_PREFIX_PATH="%ROOT%/build/vcpkg_installed/x64-windows" ^
		-DSDLSHADERCROSS_DXC=ON -DSDLSHADERCROSS_VENDORED=ON -DSDLSHADERCROSS_SHARED=OFF ^
		-DSDLSHADERCROSS_STATIC=ON -DSDLSHADERCROSS_SPIRVCROSS_SHARED=OFF -DSDLSHADERCROSS_CLI=ON ^
		-DSDLSHADERCROSS_CLI_STATIC=OFF -DSDLSHADERCROSS_INSTALL=OFF -DSDLSHADERCROSS_TESTS=OFF -DSPIRV_SKIP_TESTS=ON || exit /b 1
	rem (half the CPUs: DXC's LLVM is heavy on memory)
	set /a JOBS=%NUMBER_OF_PROCESSORS% / 2
	call cmake --build build/shadercross --target shadercross -j %%JOBS%% || exit /b 1
	rem (shadercross.exe runs from there, beside the DLLs it loads)
	copy /y build\vcpkg_installed\x64-windows\bin\SDL3.dll build\shadercross\ >nul || exit /b 1
	copy /y build\shadercross\external\DirectXShaderCompiler\bin\dxcompiler.dll build\shadercross\ >nul || exit /b 1
)

cmake --build build/game -j %NUMBER_OF_PROCESSORS% || exit /b 1
echo ready: build\game\tyrian3d.exe
