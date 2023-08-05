<p align="center"><img src="html-src/images/high_res/logo_horizontal.png" alt="PySol FC logo" height="180px"></p>

# PySol Fan Club edition

This is an open source and portable (Windows, Linux and Mac OS X) collection
of Card Solitaire/Patience games written in Python. Its homepage is
https://pysolfc.sourceforge.io/.

The maintenance branch of PySol FC on GitHub by [Shlomi
Fish](https://www.shlomifish.org/) and by some other
people, has gained official status, ported the code to Python 3,
and implemented some other enhancements.

## Install & play instructions (Linux)

_(May work on MacOS as well)_

First, clone this repository.

```bash
# This will create a folder "PySolFC"
git clone https://github.com/SummerPeng0223/PySolFC.git
```

To play the game you first need to run the setup script.

```bash
# Go to the cloned repository folder
cd PySolFC

# Run the setup
# May take 1-2 minutes to complete!
./setup.sh
```

To play the game simply run the following command.

```bash
# You must be inside the `PySolFC` folder!
./play.sh
```

## Troubleshooting

### ImportError libtk8 (Linux specific issue)

If you get the following error:

```
ImportError: libtk8.6.so: cannot open shared object file: No such file or directory
```

Then use one of the following commands to install the missing dependency:

If you are on Ubuntu:

```bash
sudo apt-get install tk
```

If you are on Arch:
```bash
sudo pacman -S tk
```

If you are on Fedora:
```bash
sudo dnf install tk
```
