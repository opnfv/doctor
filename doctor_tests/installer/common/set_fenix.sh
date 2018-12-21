#!/usr/bin/env bash

##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Config files
echo "[DEFAULT]" > fenix.conf
echo "[DEFAULT]" > fenix-api.conf
echo "port = 12347" >> fenix.conf
echo "port = 12347" >> fenix-api.conf
grep -m1 "^transport" /var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf >> fenix.conf
grep -m1 "^transport" /var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf >> fenix-api.conf
echo "[database]" >> fenix.conf
MYSQLIP=`grep -m1 "^connection=mysql" /var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf | sed -e "s/.*@//;s/\/.*//"`
echo "connection=mysql+pymysql://fenix:fenix@$MYSQLIP/fenix?read_default_group=tripleo&read_default_file=/etc/my.cnf.d/tripleo.cnf" >> fenix.conf

# Mysql pw
MYSQLPW=`cat /var/lib/config-data/mysql/etc/puppet/hieradata/service_configs.json | grep mysql | grep root_password | awk -F": " '{print $2}' | awk -F"\"" '{print $2}'`

# Fenix DB
[ `mysql -uroot -p$MYSQLPW -e "SELECT host, user FROM mysql.user;" | grep fenix | wc -l` -eq 0 ] && {
    mysql -uroot -p$MYSQLPW -hlocalhost -e "CREATE USER 'fenix'@'localhost' IDENTIFIED BY 'fenix';"
    mysql -uroot -p$MYSQLPW -hlocalhost -e "GRANT ALL PRIVILEGES ON fenix.* TO 'fenix'@'' identified by 'fenix';FLUSH PRIVILEGES;"
}
mysql -ufenix -pfenix -hlocalhost -e "DROP DATABASE IF EXISTS fenix;"
mysql -ufenix -pfenix -hlocalhost -e "CREATE DATABASE fenix CHARACTER SET utf8;"

# Remove previous container
for img in `docker image list | grep "^fenix" | awk '{print $1}'`; do
    for dock in `docker ps --all -f "ancestor=$img" | grep "$img" | awk '{print $1}'`; do
        docker stop $dock; docker rm $dock;
    done;
    docker image rm $img;
done

# Build Fenix container and run it
chmod 700 run
docker build --build-arg OPENSTACK=master --build-arg BRANCH=master --network host /home/heat-admin -t fenix | tail -1
docker run --network host -d --name fenix -p 12347:12347 -ti fenix
if [ $? -eq 0 ]; then
    echo "Fenix start: OK"
else
    echo "Fenix start: FAILED"
fi
# To debug check log from fenix container
# docker exec -ti fenix tail -f /var/log/fenix-engine.log
