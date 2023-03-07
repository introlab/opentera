echo "Create or update conda venv"
conda install -m -c conda-forge -y --copy -p $PWD/venv python=3.9
echo "Activating venv"
conda activate $PWD/venv
echo "Installing requirements"
$PWD/venv/bin/pip install -r $PWD/requirements.txt
echo "Patching protobuf until new OpenTera package release"
$PWD/venv/bin/pip uninstall --yes protobuf
$PWD/venv/bin/pip install protobuf==4.21.12
