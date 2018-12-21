FROM gliderlabs/alpine:3.5

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
        python-dev python3-dev build-base linux-headers libffi-dev \
        openssl-dev libjpeg-turbo-dev && \
    curl https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$OPENSTACK > upper-constraints.txt && \
    pip install --upgrade pip  && \
    pip install alembic aodhclient ast decorator \
        eventlet flask Flask-RESTful importlib \
        keystoneauth1 logging python-novaclient oslo.config oslo.db \
        oslo.log oslo.messaging oslo.serialization oslo.service \
        oslotest oslo.utils pbr pymysql setuptools six sqlalchemy \
        wsgiref -cupper-constraints.txt && \
    git clone https://git.openstack.org/openstack/fenix -b $BRANCH /fenix && \
    rm -fr /var/tmp/fenix
COPY run /fenix
COPY overcloudrc /fenix
WORKDIR /fenix
RUN python setup.py install
CMD ./run
