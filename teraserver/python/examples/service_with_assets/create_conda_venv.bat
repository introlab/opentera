@ECHO OFF
call conda install -m -c conda-forge -y --copy -p venv python=3.9
call conda activate .\venv
call pip install -r requirements.txt
call pip uninstall --yes protobuf
call pip install protobuf==4.21.12
call conda deactivate

