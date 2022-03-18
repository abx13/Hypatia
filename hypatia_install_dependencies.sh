# Main information
echo "Hypatia: installing dependencies"
echo ""
echo "It is highly recommend you use a recent Linux operating system (e.g., Ubuntu 20 or higher)."
echo "Python version 3.8+ is required."
echo ""

# General
sudo apt-get update || exit 1

#check python3.8+
versionPython=$(python --version)
versionPython=${versionPython:6:4}
if [[ "${versionPython:0:1}" < 3 ]];then
echo "we recommend installing python-is-python3 module if you don't need python2\
	otherwise you can replace 'python' by 'python3' everywhere "
echo "proceed to python-is-python3 installation ? [y/n]"
read r
if [[ "$r" == "y" ]]; then
sudo apt install python-is-python3 || exit 1
else echo "python is not replaced by python3, quit"; exit 1
fi
fi

if (( "${versionPython:2}" < "8" )); then
echo "please upgrade python to python 3.8+"
exit 1
fi


# satgenpy
echo "Installing dependencies for satgenpy..."
pip install numpy astropy ephem networkx sgp4 geopy matplotlib statsmodels || exit 1
sudo apt-get install libproj-dev proj-data proj-bin libgeos-dev || exit 1
# Mac alternatives (to be able to pip install cartopy)
# brew install proj geos
# export CFLAGS=-stdlib=libc++
# MACOSX_DEPLOYMENT_TARGET=10.14
pip install git+https://github.com/snkas/exputilpy.git@v1.6 || exit 1
pip install cartopy || exit 1

# ns3-sat-sim
echo "Installing dependencies for ns3-sat-sim..."
sudo apt-get -y install openmpi-bin openmpi-common openmpi-doc libopenmpi-dev lcov gnuplot || exit 1
pip install numpy statsmodels || exit 1
pip install git+https://github.com/snkas/exputilpy.git@v1.6 || exit 1
#git submodule update --init --recursive || exit 1 #no more submodules. erroneous command, basic-sim module must have an older HEAD. 

# satviz
echo "There are currently no dependencies for satviz."

# paper
echo "Installing dependencies for paper..."
pip install numpy || exit 1
pip install git+https://github.com/snkas/exputilpy.git@v1.6 || exit 1
pip install git+https://github.com/snkas/networkload.git@v1.3 || exit 1
sudo apt-get install gnuplot

# Confirmation dependencies are installed
echo ""
echo "Hypatia dependencies have been installed."
