# OpenCV

Pixel BGR Value render font issue 

# 1. Create the exact internal site-package directory your logs are looking for
mkdir -p /home/rxx02/.pyenv/versions/3.12.12/lib/python3.12/site-packages/cv2/qt/fonts

# 2. Make sure your local Linux system has standard fonts installed
sudo apt update && sudo apt install fonts-dejavu fontconfig -y

# 3. Create a direct symbolic link to route system fonts into OpenCV's directory path
ln -s /usr/share/fonts/truetype/dejavu/* /home/rxx02/.pyenv/versions/3.12.12/lib/python3.12/site-packages/cv2/qt/fonts/

