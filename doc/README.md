# Setting Up your Raspberry Pi
These instructions are for Ubuntu 21.04 or later on Raspberry Pi. Other than service setup, they should be applicable to any debian-based, reasonably recent OS (such as Raspbian, or whatever they're calling it now).

## The Basics
Install Ubuntu Server 21.04 or later: https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi#1-overview 

SSH into your new, up-and-running RPi using "ubuntu/ubuntu". Change the password.

Create a new user (here we're creating a user "cubey"):

    sudo adduser cubey
    sudo adduser cubey sudo

(Optional) Enable passwordless login: https://linuxize.com/post/how-to-setup-passwordless-ssh-login/ 

SSH into your RPi as the new user you just created.

**Slow SSH logins?** Disable PAM auth: change `UsePAM` from `yes` to `no` in */etc/ssh/sshd_config*

    UsePAM no

(Optional) change the hostname in */etc/hostname*

(Optional) set the timezone: `sudo dpkg-reconfigure tzdata`

(Optional) install zsh: `sudo apt install zsh`

(Optional) set zsh as your default shell: `chsh -s $(which zsh)`

(Optional) install oh-my-zsh: `sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

Update to latest of everything: 

    sudo apt update
    sudo apt dist-upgrade

Now would be a good time to reboot the RPi (using `sudo reboot`), and reconnect.

## Install Python (3.9):

    sudo apt install -y build-essential python3-setuptools software-properties-common python3.9 python3.9-venv python3.9-dev python3-pip v4l-utils

Set python 3.9 as the default for python3

    cd /usr/bin

    sudo rm aarch64-linux-gnu-python3-config pdb3 pydoc3 pygettext3 python3 python3-config

    sudo sh -c 'ln -s aarch64-linux-gnu-python3.9-config aarch64-linux-gnu-python3-config && \
    ln -s pdb3.9 pdb3 && \
    ln -s pydoc3.9 pydoc3 && \
    ln -s pygettext3.9 pygettext3 && \
    ln -s python3.9 python3 && \
    ln -s python3.9-config python3-config'

## Install OpenCV
    sudo apt install -y python3-opencv

## Install GPIO support
    sudo apt install python3-rpi.gpio python3-lgpio

## Install PIGPio
    cd
    wget https://github.com/joan2937/pigpio/archive/master.zip
    unzip master.zip
    cd pigpio-master
    make
    sudo make install
    sudo touch /lib/systemd/system/pigpiod.service

Add the following to /lib/systemd/system/pigpiod.service:

    [Unit]
    Description=Daemon required to control GPIO pins via pigpio
    [Service]
    ExecStart=/usr/local/bin/pigpiod
    ExecStop=/bin/systemctl kill -s SIGKILL pigpiod
    Type=forking
    [Install]
    WantedBy=multi-user.target

Setup pigpio to run at startup:

    sudo systemctl enable pigpiod

Reboot again, and reconnect.

## Install cubey
    cd
    git clone https://github.com/xoxota99/cubey.git

## Install cubey dependencies: 
    sudo pip install -r cubey/requirements.txt

This includes:
* The [kociemba](https://pypi.org/project/kociemba/) solver library
* [flask](https://flask.palletsprojects.com/en/2.0.x/) web development framework
* [pillow](https://pillow.readthedocs.io/en/stable/) image library.
* [greenlet](https://greenlet.readthedocs.io/en/latest/) concurrent process library
* Prebuilt [OpenCV libraries](https://pypi.org/project/opencv-python/) for python
* Prebuilt [OpenCV addons](https://pypi.org/project/opencv-contrib-python/) for python

## Enable shutdown button and power LED (Optional)
In */boot/firmware/config.txt*, add the following:

    dtoverlay=gpio-poweroff,gpiopin=14
    dtoverlay=gpio-shutdown,gpio_pin=4,active_low=1

and comment out `enable_uart=1`
