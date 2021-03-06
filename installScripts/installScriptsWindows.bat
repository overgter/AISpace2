@setlocal enableextensions
@cd /d "%~dp0"
echo Make sure you have installed pip and Node.js.
pause
cd ..
echo Installing jupyterlab ...
call pip3 install --upgrade jupyterlab
echo Installing ipywidgets ...
call pip3 install --upgrade ipywidgets
echo Installing AISpace2 library ...
cd js
call npm install
cd ..
call pip3 install -r requirements-dev.txt
call pip3 install -e .
echo Installing Jupyter labextension ...
jupyter labextension install @jupyter-widgets/jupyterlab-manager
cd js
echo Building AISpace2 frontend ...
call npm run update-lab-extension
jupyter labextension install
cd ..
jupyter lab