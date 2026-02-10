#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/objdetect.hpp> 
#include <chrono> 
#include <thread>
#include <cstdlib> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fstream>
#include <atomic> // Para variables compartidas entre hilos

using namespace std;
using namespace cv;

// Variable global para saber si el sistema está ocupado enviando
// atomic garantiza que no haya conflictos entre hilos
atomic<bool> sistemaOcupado(false);

void enviarSenalSocketBackground() {
    // 1. ESPERA DE SEGURIDAD
    this_thread::sleep_for(chrono::seconds(1)); // 1 seg es suficiente ahora

    // 2. TRUCO DE INGENIERÍA: RENOMBRADO ATÓMICO
    // Movemos el temporal al nombre final. Esto garantiza que 'alerta.mp4'
    // aparezca de golpe, completo y sin errores.
    cout << ">> [Background] Finalizando archivo de video..." << endl;
    rename("temp_video.mp4", "alerta.mp4"); 

    // 3. ENVIAR SOCKET
    int sock = 0;
    struct sockaddr_in serv_addr;
    string mensaje = "ANALIZAR";

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) >= 0) {
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(65432);
        if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) > 0) {
            if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) >= 0) {
                send(sock, mensaje.c_str(), mensaje.length(), 0);
                cout << ">> [Background] Señal enviada a Python." << endl;
            }
        }
        close(sock);
    }
    
    // 4. COOLDOWN (Tiempo para que Python trabaje tranquilo)
    this_thread::sleep_for(chrono::seconds(8));
    
    sistemaOcupado = false; 
    cout << ">> [Background] Sistema listo." << endl;
}

string obtenerUsoMemoria() {
    ifstream archivo("/proc/self/status");
    string linea;
    while (getline(archivo, linea)) {
        if (linea.substr(0, 6) == "VmRSS:") return linea;
    }
    return "Mem: N/A";
}

int main() {
    VideoCapture video(0); 
    if(!video.isOpened()) return -1;

    CascadeClassifier detector;
    if( !detector.load("modelo_final/cascade.xml") ) {
        cout << "Error: No encuentro cascade.xml" << endl;
        return -1;
    }

    Mat frame, gray;
    bool grabando = false;
    int framesGrabados = 0;
    int maxFrames = 100; // 5 segundos de grabación aprox
    VideoWriter grabador;

    // Variables FPS
    double fps = 0;
    int frameCounter = 0;
    auto start_time = chrono::high_resolution_clock::now();

    cout << "--- CENTINELA FLUIDO (MULTITHREADING) ---" << endl;

    while(true){
        video >> frame;
        if (frame.empty()) break;

        // Proceso Básico
        cvtColor(frame, gray, COLOR_BGR2GRAY);
        equalizeHist(gray, gray);

        // --- LÓGICA DE DETECCIÓN INTELIGENTE ---
        // Solo detectamos si NO estamos grabando y el sistema NO está ocupado enviando
        if (!grabando && !sistemaOcupado) {
            vector<Rect> personas;
            detector.detectMultiScale(gray, personas, 1.1, 5, 0, Size(30, 60));

            for(auto& r : personas) {
                rectangle(frame, r, Scalar(0, 255, 0), 2);
            }

          // ... dentro del if (personas.size() > 0) ...
            if (personas.size() > 0) {
                cout << "¡INTRUSO! Iniciando grabación..." << endl;
                imwrite("captura_original.jpg", frame); 
                
                grabando = true;
                framesGrabados = 0;
                
                // CAMBIO AQUÍ: Grabamos en un archivo TEMPORAL
                // Usamos 'temp_video.mp4' en lugar de 'alerta.mp4'
                grabador.open("temp_video.mp4", VideoWriter::fourcc('m','p','4','v'), 
                              20.0, frame.size(), true);
                
                sistemaOcupado = true;
            }
        }

        // --- LÓGICA DE GRABACIÓN ---
        if (grabando) {
            grabador.write(frame); 
            putText(frame, "REC", Point(frame.cols-50, 30), FONT_HERSHEY_SIMPLEX, 0.8, Scalar(0,0,255), 2);
            framesGrabados++;

            if (framesGrabados >= maxFrames) {
                cout << "Grabación finalizada. Procesando en segundo plano..." << endl;
                grabando = false;
                grabador.release(); // Cierra el archivo
                
                // --- MAGIA: LANZAR HILO INDEPENDIENTE ---
                // Esto crea un "trabajador fantasma" que espera los 2 segundos y avisa a Python.
                // El bucle principal (while) SIGUE CORRIENDO INMEDIATAMENTE.
                thread t(enviarSenalSocketBackground);
                t.detach(); 
            }
        } else {
            // Si el sistema está ocupado (Python trabajando), mostramos aviso
            if (sistemaOcupado) {
                putText(frame, "PROCESANDO ALERTA...", Point(10, 100), FONT_HERSHEY_SIMPLEX, 0.6, Scalar(0,255,255), 2);
            }
        }

        // --- HUD (Siempre visible) ---
        frameCounter++;
        auto current_time = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = current_time - start_time;
        if(elapsed.count() >= 1.0) {
            fps = frameCounter / elapsed.count();
            frameCounter = 0;
            start_time = current_time;
        }
        
        rectangle(frame, Point(0,0), Point(200, 60), Scalar(0,0,0), -1);
        putText(frame, "FPS: " + to_string((int)fps), Point(10, 20), FONT_HERSHEY_SIMPLEX, 0.6, Scalar(0,255,0), 1);
        putText(frame, obtenerUsoMemoria(), Point(10, 45), FONT_HERSHEY_SIMPLEX, 0.5, Scalar(0,255,255), 1);

        imshow("Proyecto II - Camara Fluida", frame);
        if(waitKey(30) == 27) break; 
    }
    return 0;
}