#!/usr/bin/env bash

##############################################################################
# Copyright (c) 2019 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Config files
docker -v >/dev/null || {
echo "Fenix needs docker to be installed..." 
ver=`grep "UBUNTU_CODENAME" /etc/os-release | cut -d '=' -f 2`
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $ver stable"
apt install apt-transport-https ca-certificates curl software-properties-common
apt update
apt-cache policy docker-ce
apt-get install -y docker-ce docker-ce-cli containerd.io
dpkg -r --force-depends golang-docker-credential-helpers
}

docker ps | grep fenix -q && {
REMOTE=`git ls-remote  https://opendev.org/x/fenix HEAD | awk '{ print $1}'`
LOCAL=`docker exec -t fenix git rev-parse @`
if [[ "$LOCAL" =~ "$REMOTE" ]]; then
    # Difference in above string ending marks, so cannot compare equal
    echo "Fenix start: Already running latest $LOCAL equals $REMOTE"
    exit 0
else
    echo "Fenix container needs to be recreated $LOCAL not $REMOTE"
    # Remove previous container
    for img in `docker image list | grep "^fenix" | awk '{print $1}'`; do
        for dock in `docker ps --all -f "ancestor=$img" | grep "$img" | awk '{print $1}'`; do
            docker stop $dock; docker rm $dock;
        done;
        docker image rm $img;
    done
fi
} || echo "Fenix container needs to be created..."

cp /root/keystonercv3 .

transport=`grep -m1 "^transport" /etc/nova/nova.conf`
. keystonercv3

echo "[DEFAULT]" > fenix.conf
echo "port = 12347" >> fenix.conf
echo $transport >> fenix.conf

echo "[database]" >> fenix.conf
MYSQLIP=`grep -m1 "^connection" /etc/nova/nova.conf | sed -e "s/.*@//;s/\/.*//"`
echo "connection = mysql+pymysql://fenix:fenix@$MYSQLIP/fenix" >> fenix.conf

echo "[service_user]" >> fenix.conf
echo "os_auth_url = $OS_AUTH_URL" >> fenix.conf
echo "os_username = $OS_USERNAME" >> fenix.conf
echo "os_password = $OS_PASSWORD" >> fenix.conf
echo "os_user_domain_name = $OS_USER_DOMAIN_NAME" >> fenix.conf
echo "os_project_name = $OS_PROJECT_NAME" >> fenix.conf
echo "os_project_domain_name = $OS_PROJECT_DOMAIN_NAME" >> fenix.conf

echo "[DEFAULT]" > fenix-api.conf
echo "port = 12347" >> fenix-api.conf
echo $transport >> fenix-api.conf

echo "[keystone_authtoken]" >> fenix-api.conf
echo "auth_url = $OS_AUTH_URL" >> fenix-api.conf
echo "auth_type = password" >> fenix-api.conf
echo "project_domain_name = $OS_PROJECT_DOMAIN_NAME" >> fenix-api.conf
echo "project_name = $OS_PROJECT_NAME" >> fenix-api.conf
echo "user_domain_name = $OS_PROJECT_DOMAIN_NAME" >> fenix-api.conf
echo "password = $OS_PASSWORD" >> fenix-api.conf
echo "username = $OS_USERNAME" >> fenix-api.conf
echo "cafile = /opt/stack/data/ca-bundle.pem" >> fenix-api.conf

openstack service list | grep -q maintenance || {
openstack service create --name fenix --enable maintenance
openstack endpoint create --region $OS_REGION_NAME --enable fenix public http://localhost:12347/v1
}

# Mysql pw
# MYSQLPW=`cat /var/lib/config-data/mysql/etc/puppet/hieradata/service_configs.json | grep mysql | grep root_password | awk -F": " '{print $2}' | awk -F"\"" '{print $2}'`
MYSQLPW=root

# Fenix DB
[ `mysql -uroot -p$MYSQLPW -e "SELECT host, user FROM mysql.user;" | grep fenix | wc -l` -eq 0 ] && {
    mysql -uroot -p$MYSQLPW -hlocalhost -e "CREATE USER 'fenix'@'localhost' IDENTIFIED BY 'fenix';"
    mysql -uroot -p$MYSQLPW -hlocalhost -e "GRANT ALL PRIVILEGES ON fenix.* TO 'fenix'@'' identified by 'fenix';FLUSH PRIVILEGES;"
}
mysql -ufenix -pfenix -hlocalhost -e "DROP DATABASE IF EXISTS fenix;"
mysql -ufenix -pfenix -hlocalhost -e "CREATE DATABASE fenix CHARACTER SET utf8;"

# Build Fenix container and run it
chmod 700 run
docker build --build-arg OPENSTACK=master --build-arg BRANCH=master --network host $PWD -t fenix | tail -1
docker run --network host -d --name fenix -p 12347:12347 -ti fenix
if [ $? -eq 0 ]; then
    echo "Fenix start: OK"
else
    echo "Fenix start: FAILED"
fi
# To debug check log from fenix container
# docker exec -ti fenix tail -f /var/log/fenix-engine.log
