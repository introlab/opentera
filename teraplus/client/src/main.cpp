/*
 * main.cpp
 *
 */
#include "ClientApp.h"
#include <QWebEngineSettings>

int main(int argc, char* argv[])
{
    int rval;
    // Force use of ANGLE instead of Desktop OpenGL - some memory leak may happen with WebRTC on Intel Graphics Cards otherwise.
    QApplication::setAttribute(Qt::AA_UseOpenGLES, true);
    QApplication::setAttribute(Qt::AA_EnableHighDpiScaling, true);

    ClientApp* app = new ClientApp(argc, argv);

    //Set application style
    #ifndef WIN32 // Don't set style on Windows - it creates some issues with combobox look.
    //app->setStyle("windows");
    #endif


    //WebEngine default Settings
    /*QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::PluginsEnabled, true);
    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::JavascriptEnabled, true);
    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::JavascriptCanOpenWindows, true);*/

    rval = app->exec();

    delete app;

    return rval;
}
