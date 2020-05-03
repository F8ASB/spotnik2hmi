#stamp=date(%Y%m%d)
mv fonctions.py /opt/spotnik/spotnik2hmi/old_version/fonctions`date +%d%m%Y`.py
mv spotnik2hmi.py /opt/spotnik/spotnik2hmi/old_version/spotnik2hmi`date +%d%m%Y`.py
mv install.sh /opt/spotnik/spotnik2hmi/old_version/install`date +%d%m%Y`.sh

wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi/master/fonctions.py
wget  https://raw.githubusercontent.com/F8ASB/spotnik2hmi/master/spotnik2hmi.py
wget  https://raw.githubusercontent.com/F8ASB/spotnik2hmi/master/install.sh

https://raw.githubusercontent.com/F8ASB/spotnik2hmi/master/datas/icao.cfg

#maj icao
wget -N -P /opt/spotnik/spotnik2hmi/datas/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi/master/datas/icao.cfg

