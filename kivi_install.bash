
sudo apt update
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev

sudo pip3 install Cython
python3 -m pip install --user https://github.com/kivy/kivy/archive/master.zip

sudo apt install xserver-xorg xinit


git clone https://github.com/kivy/kivy
cd kivy

make
echo "export PYTHONPATH=$(pwd):\$PYTHONPATH" >> ~/.profile
source ~/.profile

sudo pip3 install keyboard
sudo pip3 install pymediainfo

------------------------------------------------

sudo apt update
sudo apt install python3-venv
sudo pip3 install Cythonpip

sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev

python .m venv ~/kivy_env
sudo pip3 install pymediainfo
sudo apt install libmediainfo0v5
pip install evdev
sudo usermod  -aG input pi
sudo apt-get install xorg

--< then enabled vnc with raspi.config

sudo apt install mpv
