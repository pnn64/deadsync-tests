# Resource cleanup

The initial inspection proved two obsolete host transfer copies were identical
in size and SHA-256 to retained guest binaries, were ordinary files without
open handles, and could be removed. The completed receipt records 498,261,624
logical bytes and 498,270,208 allocated bytes reclaimed. Other artifacts were
retained when duplication or obsolescence was not established.

After the final all-15 pinned-B checkpoint, the idle-worker inspection found no
capture/replay/build/transfer processes and no logged-in users on fourteen unused
workers and builder1516. The only task services running on those workers were
unused Xvfb displays. Each guest was rechecked immediately before graceful
shutdown. All fifteen stopped successfully; no force stop or disk deletion was
used. This released 131,072 MiB (128 GiB) of configured VM memory. Observed host
MemAvailable rose from 87,634,259,968 to 209,114,300,416 bytes over that interval.
The latter is a host observation, not a claim that every byte is attributable
to shutdown.

VM1503 remained active for the new native controls and fixture packing at this
checkpoint. Template1500 and all guest backing disks were retained. Other VMs
and containers were not modified. The final collection before shutdown is bound
by SHA-256 546c9b576e4a90023530d0be5deeb2fe52ef8667f95d8375508ec7a100010e35.

The ZIP retains both inspections, the reviewed scripts, individual shutdown
receipts, final VM status, and exact member hashes. Every archived member was
verified after transfer.
