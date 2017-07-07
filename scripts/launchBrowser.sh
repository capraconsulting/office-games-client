#/bin/bash

# Disable DPMS / Screen blanking
xset -dpms
xset s off
xset s noblank

rm -rf /root/.config
mkdir -p /root/.config
url=$OG_VIEWER_URL
default='https://capraconsulting.no'
sudo matchbox-window-manager -use_titlebar no -use_cursor no &
xte 'sleep 15' 'key F11'&
python /usr/src/app/run.py &
iceweasel ${url:-$default}
unclutter -idle 0
sleep 2s
