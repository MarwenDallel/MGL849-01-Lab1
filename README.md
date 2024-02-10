# Prérequis
    sudo apt update
    sudo apt install default-jdk
    sudo apt install python3-dev sense-hat
    
# Créer un environnement virtuel
    python -m venv venv
    source ./venv/bin/activate

# Installer les prérequis Python
    pip install -r requirements.txt

# Setup RTIMULib
    git clone https://github.com/RPi-Distro/RTIMULib/RTIMU
    python setup.py build
    python setup.py install

# Démarrer le programme d'affichage
    java -jar Lab1Afficheur.jar

# Démarrer le programme sense hat
    python sense_socket.py
