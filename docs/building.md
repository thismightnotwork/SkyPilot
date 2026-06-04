# Building SkyHigh Pilot

## Prerequisites
- CMake 3.24+
- Qt 6.5+
- A C++20 compiler (MSVC 2022, GCC 13, Clang 16)
- vcpkg (optional, for protobuf)

## Steps
```bash
cmake -B build -G Ninja
cmake --build build
```

## Windows
Install Qt6 via the Qt online installer. Set `Qt6_DIR` in CMake if not auto-detected.
