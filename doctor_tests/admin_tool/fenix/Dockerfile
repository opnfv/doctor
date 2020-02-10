FROM gliderlabs/alpine:3.6

ARG BRANCH=master
ARG OPENSTACK=master

EXPOSE 12347

RUN echo "Building Fenix container against OpenStack $OPENSTACK" && \
    echo "Building Fenix with $BRANCH" && \
    mkdir /etc/fenix && \
    mkdir -p /var/tmp/fenix
WORKDIR /var/tmp/fenix
COPY fenix*.conf /etc/fenix/

RUN apk --no-cache add ca-certificates && \
    apk --no-cache add --update python3 sshpass py-pip git curl  && \
    apk --no-cache add --virtual .build-deps --update \
        python3-dev build-base linux-headers libffi-dev \
        openssl-dev libjpeg-turbo-dev && \
    curl https://opendev.org/openstack/requirements/raw/branch/$OPENSTACK/upper-constraints.txt > upper-constraints.txt && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    pip3 install --upgrade pip && \
    pip3 install alembic aodhclient decorator flask Flask-RESTful eventlet jsonschema \
        keystoneauth1 keystonemiddleware python-novaclient oslo.config pecan \
        oslo.db oslo.log oslo.messaging oslo.serialization oslo.service oslo_policy \
        oslotest oslo.utils pbr pymysql six sqlalchemy -cupper-constraints.txt && \
    git clone https://opendev.org/x/fenix -b $BRANCH /fenix && \
    rm -fr /var/tmp/fenix
COPY run /fenix
COPY keystonercv3 /fenix
WORKDIR /fenix
RUN python3 setup.py install
CMD ./run
