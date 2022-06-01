# Miniconda installation and environment configuration
CONDA_URL=https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
# Should you want to try and install this repository on Windows or macOS
# (untested), here are the links to the relevant Miniconda installer:
# Macos: https://repo.anaconda.com/miniconda/Miniconda-2.2.2-MacOSX-x86_64.sh
# Windows: https://repo.anaconda.com/miniconda/Miniconda-2.2.8-Windows-x86_64.exe
test -f miniconda.sh || wget $CONDA_URL -O miniconda.sh
test -d tools/speechbrain_python || bash miniconda.sh -b -p tools/speechbrain_python
conda deactivate
. tools/speechbrain_python/bin/activate && conda install -y setuptools -c anaconda
. tools/speechbrain_python/bin/activate && conda install -y pip -c anaconda
. tools/speechbrain_python/bin/activate && conda update -y conda
. tools/speechbrain_python/bin/activate && conda install -y python=3.8
. tools/speechbrain_python/bin/activate && conda info -a

# Setting up the new virtual python environment
source tools/speechbrain_python/bin/activate && pip install -U pip
source tools/speechbrain_python/bin/activate && pip install -e .
source tools/speechbrain_python/bin/activate && pip install -r requirements.txt