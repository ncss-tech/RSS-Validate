# RSS-Validate
Tools to validate RSS packages prior to uploading to Box

This tool will walk through a top directory and check for:
a properly formatted package (e.g. RSS_FL and RSS_FL.gdb)
a suitably named MapunitRaster_10m_datestamp (gdb and tif)
metadata for tifas MapunitRaster_10m_datestamp.xml
MapunitRaster_10m_datestamp is unsigned 32 bit
MapunitRaster_10m_datestamp has NoData value 2147483647 (tif only, gdb raster does not have NoData value exposed)
proper spatial reference (32161, 5070, 3338, 4326)
required text files in open source package (no extraneous)
required gdb tables (no extraneous)
mukeys in raster (tif/gdb) match mukeys in text/gdb tables




