@ECHO OFF
call conda install -m -c conda-forge -y --copy -p venv python=3.11
call conda activate .\venv
call pip install -r requirements.txt
call conda deactivate

