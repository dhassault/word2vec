

echo "Recommended tool for installing Python packages for python2.7:"
sudo apt-get install python-pip 

echo "For optimized python libraries:"
sudo apt-get install libopenblas-dev liblapack-dev python-dev gfortran

echo "Download numpy, fundamental package for scientific computing:"
pip install -d ./ numpy
tar -zxvf numpy-1.11.0.tar.gz

python2.7 ./numpy-1.11.0/setup.py install

echo "Scipy, Python-based ecosystem of open-source software for mathematics:"
pip install scipy

echo "Now we install gensim and all dependecies:"
pip install gensim

echo "And the similarities server:"
pip install simserver


