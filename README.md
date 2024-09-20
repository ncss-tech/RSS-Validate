# RSS-Validate
Tools to validate RSS packages prior to uploading to Box

This tool will walk through a top directory and check for:

* a properly formatted package (e.g. RSS_FL and RSS_FL.gdb)
* a suitably named MURASTER_10m_<ST>_<yyyy> (gdb and tif)
* metadata for tif as MURASTER_10m_<ST>_<yyyy>.xml
* MURASTER_10m_<ST>_<yyyy> is unsigned 32 bit
* MURASTER_10m_<ST>_<yyyy> has NoData value 2147483647 (tif only, gdb raster does not have NoData value exposed)
* proper spatial reference (32161, 5070, 3338, 4326)
* required text files in open source package (no extraneous)
* required gdb tables (no extraneous)
* mukeys in raster (tif/gdb) match mukeys in text/gdb tables

you can run as ArcTool Box in ArcGIS Pro (ArcGIS Desktop has a bug) or run natively in python by commenting line 315 out and uncommneting 316 and providing a directory path




