Doctor Plugin for Fuel
============

Doctor plugin
-----------------------

Overview
--------

This will install Doctor onto the OpenStack controller for Fault Management for Virtual Infrastructure

* [OPNFV Doctor](https://wiki.opnfv.org/doctor) Fault Management

Requirements
------------

| Requirement                      | Version/Comment |
|----------------------------------|-----------------|
| Mirantis OpenStack compatibility | 9.0             |

Recommendations
---------------

None.

Installation Guide
==================

Doctor plugin installation
----------------------------------------

1. Clone the fuel-plugin-doctor repo from github:

        git clone https://github.com/openzero-zte/fuel-plugin-doctor.git

2. Install the Fuel Plugin Builder:

        pip install fuel-plugin-builder

3. Build Doctor Fuel plugin:

        fpb --build fuel-plugin-doctor/

4. The *fuel-plugin-doctor-x.x-x.rpm* plugin package will be created in the plugin folder.

5. Move this file to the Fuel Master node with secure copy (scp):

        scp fuel-plugin-doctor-x.x-x.rpm root@<the_Fuel_Master_node_IP address>:/tmp

6. While logged in Fuel Master install the Doctor plugin:

        fuel plugins --install /tmp/fuel-plugin-doctor-x.x-x.rpm

7. Check if the plugin was installed successfully:

        fuel plugins

        id | name                | version | package_version
        ---|---------------------|---------|----------------
        1  | fuel-plugin-doctor  | 1.0.0   | 1.0.0

8. Plugin is ready to use and can be enabled on the Settings tab of the Fuel web UI.

## License
  [Apache-2.0](LICENSE)
