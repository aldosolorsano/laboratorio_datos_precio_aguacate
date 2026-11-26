@echo off
chcp 65001 > nul
echo =====================================================================
echo  OBSERVATORIO DE PRECIOS DEL AGUACATE - ACTUALIZACION SEMANAL
echo =====================================================================
echo.
echo [1/6] Obteniendo datos de clima (Open-Meteo)...
.venv\Scripts\python.exe src\extractores\openmeteo.py

echo.
echo [2/6] Obteniendo redes sociales en tiempo real...
.venv\Scripts\python.exe src\extractores\redes_sociales.py

echo.
echo [3/6] Procesando pipeline optimizado E3 (CSV y Parquet)...
.venv\Scripts\python.exe -m pipeline.e3

echo.
echo [4/6] Calculando proyecciones para todos los mercados mayoristas...
.venv\Scripts\python.exe -m laboratorio.pronostico

echo.
echo [5/6] Generando tablero web interactivo actualizado...
.venv\Scripts\python.exe -m laboratorio.tablero

echo.
echo [6/6] Verificando pruebas de calidad...
.venv\Scripts\pytest.exe tests\test_e1.py tests\test_e2.py tests\test_e3.py

echo.
echo =====================================================================
echo  ACTUALIZACION COMPLETADA CON EXITO.
echo  Puedes abrir el tablero actualizado en: docs\index.html
echo =====================================================================
pause
