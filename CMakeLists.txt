cmake_minimum_required(VERSION 3.24)
project(SkyHighPilot VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# ── Qt modules ──────────────────────────────────────────────────────────────
find_package(Qt6 REQUIRED COMPONENTS Core Network Qml Quick QuickControls2 Multimedia Location Positioning)

# ── Optional: MSFS SimConnect SDK ───────────────────────────────────────────
# Set SIMCONNECT_SDK_DIR to the MSFS SDK path, e.g.:
#   cmake -B build -DSIMCONNECT_SDK_DIR="C:/MSFS SDK/SimConnect SDK"
# Without this the MSFS connector compiles but does nothing at runtime.
if(DEFINED SIMCONNECT_SDK_DIR)
    message(STATUS "[SkyHigh] SimConnect SDK: ${SIMCONNECT_SDK_DIR}")
    add_compile_definitions(SKYHIGH_SIMCONNECT=1)
    include_directories("${SIMCONNECT_SDK_DIR}/include")
    link_directories("${SIMCONNECT_SDK_DIR}/lib/MSFS")
endif()

# ── Sources ─────────────────────────────────────────────────────────────────
add_executable(SkyHighPilot
    src/main.cpp
    src/app/Application.cpp
    src/core/fsd/FsdClient.cpp
    src/core/fsd/FsdProtocol.cpp
    src/core/fsd/FsdParser.cpp
    src/core/fsd/FsdPackets.cpp
    src/core/network/ConnectionManager.cpp
    src/core/traffic/TrafficManager.cpp
    src/core/messages/MessageManager.cpp
    src/core/models/AircraftModelSet.cpp
    src/core/models/ModelMatcher.cpp
    src/core/pilot/PilotSession.cpp
    src/core/pilot/FlightPlan.cpp
    src/core/voice/MumbleClient.cpp
    src/core/voice/AudioManager.cpp
    src/core/SimConnector/MsfsConnector.cpp
    src/core/SimConnector/XPlaneConnector.cpp
    src/ui/MainWindow.cpp
    src/ui/viewmodels/ConnectionViewModel.cpp
    src/utils/Logger.cpp
    src/utils/CoordUtils.cpp
    resources/qml.qrc
)

target_include_directories(SkyHighPilot PRIVATE ${CMAKE_SOURCE_DIR}/src)

target_link_libraries(SkyHighPilot PRIVATE
    Qt6::Core
    Qt6::Network
    Qt6::Qml
    Qt6::Quick
    Qt6::QuickControls2
    Qt6::Multimedia
    Qt6::Location
    Qt6::Positioning
)

if(DEFINED SIMCONNECT_SDK_DIR)
    target_link_libraries(SkyHighPilot PRIVATE SimConnect)
endif()

enable_testing()
add_subdirectory(tests)
