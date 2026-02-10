cmake_minimum_required(VERSION 3.10)
project(Proyecto_Parte2_LBP)

# 1. Estándar C++17 (Igual que en el Makefile "-std=c++17")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 2. Buscar OpenCV (Igual que los "-I" y "-L" de OpenCV del Makefile)
find_package(OpenCV REQUIRED)

# 3. Incluir directorios de cabecera (Igual que el "-I.../lbp-library/")
# Esto permite que funcione '#include "lbplibrary.hpp"'
include_directories(${CMAKE_SOURCE_DIR}/lbp-library)

# 4. Crear el ejecutable
# Aquí le decimos a CMake dónde están EXACTAMENTE los archivos .cpp
add_executable(vision.bin 
    Principal.cpp                                   # Tu código principal
    lbp-library/package_lbp/olbp/OLBP.cpp           # El archivo oculto que vimos en el Makefile
)

# 5. Vincular librerías (Igual que "-lopencv_core -lopencv_imgproc ...")
target_link_libraries(vision.bin
    ${OpenCV_LIBS}
)