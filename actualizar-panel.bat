@echo off
cd /d C:\pionier
python helpdesk_export.py || (echo ERROR EN EL EXPORT & pause & exit /b 1)
git add helpdesk.json
git commit -m "Actualizacion helpdesk %date%"
git push
echo Panel actualizado.
timeout /t 3