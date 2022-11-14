Couchcopy
=========

Create an archive of a running CouchDB node, saving CouchDB files
``data/.shards``, ``data/_dbs.couch`` and ``data/shards`` in this order.
To allow backup of a running CouchDB, files are copied before archive creation.

Restore an archive of a CouchDB node to a new CouchDB. The new CouchDB can be a
cluster of multiple nodes.
The new CouchDB configuration should already be done before using Couchcopy,
however, all existing data will be deleted.
During restoration, CouchDB will be stopped and restarted on each cluster
nodes.

Limitations
-----------

Tested with CouchDB 3.1.1 only.

To restore an archive, Couchcopy needs to stop and start CouchDB. It assumes
that CouchDB is controlled by systemd. If you don't use systemd you can
change parameters ``--couchdb-start`` and ``--couchdb-stop``.

Your CouchDB ``n`` value should be higher or equal to the number of nodes in
your CouchDB cluster.
Otherwise saving shards from one node would not be enough to save and restore
all databases.
See `CouchDB documentation
<https://docs.couchdb.org/en/3.1.1/cluster/theory.html#theory>`_ for more
details on replicas and nodes.

The number of shards per database, i.e. the value of ``q``, should be the same
for the origin CouchDB and the destination CouchDB.
Otherwise, ``tree /data/shards`` is not the same.

Couchcopy assumes you have read and write permissions on CouchDB data
directories. If you don't have them, you can try to use the ``--use-sudo``
option.

Get started
-----------

Install Couchcopy:

.. code:: shell

 pip install --user couchcopy

Make a backup to ``backup.tar.gz``, from machine ``old-server`` with CouchDB
data at ``/var/lib/couchdb``:

.. code:: shell

 couchcopy backup old-server,/var/lib/couchdb backup.tar.gz

Restore a backup ``backup.tar.gz`` to a 3-node CouchDB cluster where machines
are accessible via SSH at ``cluster_vm1``, ``cluster_vm2``, ``cluster_vm3``:

.. code:: shell

 couchcopy restore backup.tar.gz admin:password@cluster_vm1,/var/lib/couchdb \
     admin:password@cluster_vm2,/var/lib/couchdb \
     admin:password@cluster_vm3,/var/lib/couchdb

Quickly access data from a backup, by spawning a CouchDB instance:

.. code:: shell

 couchcopy load backup.tar.gz

Improve ``couchcopy load`` loading time by preconfiguring CouchDB metadata, so
that the ``Updating CouchDB metadata...`` step is not needed:

.. code:: shell

 couchcopy unbrand slow_backup.tar.gz quick_backup.tar.gz

For more options:

.. code:: shell

 couchcopy -h
 couchcopy backup -h
 couchcopy unbrand -h
 couchcopy load -h
 couchcopy restore -h

On Fedora, CouchDB can be installed and configured with the following :

.. code:: shell

 sudo dnf copr enable -y adrienverge/couchdb
 sudo dnf install couchdb
 sudo sh -c 'echo "admin = password" >> /etc/couchdb/local.ini'
 sudo systemctl restart couchdb

If you work with remote machines, CouchDB needs to listen to remote IPs on
each machine. You can enable it with the following (for security, revert it
afterwards):

.. code:: shell

 sudo sed -i 's/;bind_address = 127.0.0.1/bind_address = 0.0.0.0/g' /etc/couchdb/local.ini

Implementation details
----------------------

During restoration, if the new CouchDB nodes names are not the same as the
old CouchDB, nodes names are updated using  CouchDB ``/_node/_local/_dbs``
endpoint. See CouchDB ``/_node/_local/_dbs`` `endpoint documentation
<https://docs.couchdb.org/en/3.1.1/cluster/sharding.html#updating-cluster-metadata-to-reflect-the-new-target-shard-s>`_.

During restoration, Couchcopy first updates one CouchDB node metadata (i.e. the
list of nodes names) then it lets CouchDB itself synchronize metadata to the
other nodes.
Couchcopy exits when the synchronization is finished for all nodes, using
undocumented CouchDB ``/_dbs`` endpoint to monitor CouchDB nodes
synchronization.
You can skip that part if you want, i.e. you can exit Couchcopy safely when the
following log trace is displayed
``[Waiting for CouchDB cluster synchronization...]``.
For a CouchDB of 10^5 databases, updating the first node metadata takes 35
minutes then metadata synchronization to the other nodes takes 6 minutes.
For a CouchDB of 100 databases only, both operations are nearly instantaneous.

Developer notes
---------------

To speed up CouchDB nodes synchronization it is possible to:

- Disable compaction daemon during synchronization (for 10^5 databases, nodes
  synchronization goes from 6 minutes down to 4 minutes).
- Copy the saved ``_dbs.couch`` on every machine, but it sounds dangerous, it
  sounds better to let CouchDB rebuild these files itself (for 10^5 databases,
  nodes synchronization goes from 6 minutes down to 0 seconds).
- Machines disk IOPS consumption is around 1200 IOPS during restoration.
- Sometimes, the nodes synchronization, instead of taking 6 minutes for 10^5
  databases, takes more than 3 hours. I wasn't able to find the cause or
  eliminate this bad performance reliably. I advise using fast machines on the
  same local network, and disable compaction.
- Interesting discussions on CouchDB:

  - On nodes renaming after ``data/*`` copy for a backup restoration:

    - https://github.com/apache/couchdb/discussions/3436#discussioncomment-494504

  - On CouchDB cluster internal backfill for a backup restoration:

    - https://www.mail-archive.com/user@couchdb.apache.org/msg30003.html

  - Unanswered questions about nodes renaming speed, and backup feasibility:

    - https://www.mail-archive.com/user@couchdb.apache.org/msg29982.html
    - https://github.com/apache/couchdb/discussions/3383

Build and publish
-----------------

.. code:: shell

 python setup.py sdist
 twine upload dist/*

License
-------

This program is licensed under the GNU General Public License version 3.
