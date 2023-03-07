# Example service using assets, Flask Rest API and views

This is an example service using assets (file storage), Flask Rest API and views. The views can be developped using the 
internal templating system (jinja) or using external framework such as React or Angular. 

## Setup
Before running those setups steps, a working miniconda or a python3 environment should have been setup. See the OpenTera
wiki for more information on how to do this.

**NOTE**: Current OpenTera package on PiPy is based on **Python 3.9**. Thus, until a new release is done, this version
should be used in services.

```bash
# Create a virtual environment
python3 -m venv venv

# Enable venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

```

Virtual environment can also be created with conda (instead of python3 venv) if installed by using :

```bash
# Linux/Mac: This will create the environment and install requirements (Linux, Mac)
source ./create_conda_env.sh

# Windows: This will create the environment and install requirements
create_conda_env.bat
```

## Database pre-configuration
Create an empty database with the parameters set in the [config file](ExampleService.json) (or the parameters that are setup in your configuration)

## Running the example service

1. Create an appropriate service in the OpenTera service (using OpenTeraPlus or a similar tool). Use the parameters in 
   the config file (port, service key [name])

2. Setup the correct venv in your development environment

3. Run the "ExampleService.py" script

## Adapting the example service for your own needs

Most of the things required to do to adapt the service for your needs are in "TODO" comments in the file.
