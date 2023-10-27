echo "Create or update conda venv"
conda install -m -c conda-forge -y --copy -p $PWD/venv python=3.11
echo "Activating venv"
conda activate $PWD/venv
echo "Installing requirements"
$PWD/venv/bin/pip install -r $PWD/requirements.txt
