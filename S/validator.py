# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:43:35 2022

@author: Charles.Ferguson
"""


def insstatedir(dire=None, f=None):

    print(dire)
    # the .\FL directory is passed
    state = os.path.basename(dire)
    if state in states:
        msg2 = '\nValidataing RSS package for ' + state
        f.write(msg2 + '\n')
        direchk = ['RSS_' + state,  'RSS_' + state + '.gdb']
        if not os.listdir(dire) == direchk:
            msg2b = fail + 'Top level state ' + state + ' is missing the open source package, the gdb, or has extraneous files'
            f.write(msg2b + '\n')
        else:
            msg2b = success + 'Top level state folder ' + state + ' is valid'
            f.write(msg2b + '\n')

            # in it are 2 folders: RSS_FL, RSS_FL.gdb
            # this is the open source (non gdb folder)
            osp = dire + os.sep + 'RSS_' + state
            if not os.path.isdir(osp):
                msg3 = fail + 'non-ESRI package not located\n'
                f.write('\tOpen Source Package: ' + msg3)
            else:
                osd = os.listdir(osp)
                osdreq = ['spatial', 'tabular']
                if osd != osdreq:
                    msg3 = fail + 'structure of open source directory inconsistent\n'
                    f.write('\tOpen Source Package: ' + msg3)
                else:
                    osdspatial = os.path.join(dire, osp, 'spatial')
                    osdtabular = os.path.join(dire, osp, 'tabular')

                    osrfiles = os.listdir(osdspatial)
                    osraster = [f for f in osrfiles if f.endswith('.tif')]

                    if len(osraster) != 1:
                        msg3 = fail + 'unable to pinpoint a tif MapunitRaster_10m'
                        f.write('\tOpen Source Package: ' + msg3)
                    elif not osraster[0].startswith('MapunitRaster_10m'):
                        msg3 = fail + 'unable to locate the MapunitRaster_10m\n'
                        f.write('\tOpen Source Package: ' + msg3)
                    elif osraster[0].count("_") != 3:
                        msg3 = fail + 'unable to locate a properly identified MapunitRaster_10m_date-stamp tif raster\n'
                        f.write('\tOpen Source Package: ' + msg3)
                    else:
                        try:
                            i = osraster[0].rfind("_")
                            stamp = osraster[0][i + 1:i + 7]
                            int(stamp)
                            msg3 = success + 'located properly named tif raster ' + osraster[0] + '\n'
                            f.write('\tOpen Source Package: ' + msg3)
                        except:
                            msg3 = fail + 'unable validate date stamp for ' + osraster[0] + '\'\n'
                            f.write('\tOpen Source Package: ' + msg3)

                        # metadata
                        meta = [f for f in osrfiles if f.endswith('.tif.xml')]
                        if len(meta) == 0:
                            msg4 = fail + 'unable to locate a xml metadata file\n'
                            f.write('\tOpen Source Package: ' + msg4)
                        else:
                            msg4 = success + 'found a .tif.xml metadata file\n'
                            f.write('\tOpen Source Package: ' + msg4)

                    path = os.path.join(dire, osdspatial, osraster[0])
                    print(path)
                    desc = arcpy.Describe(path)
                    sr = desc.spatialReference
                    if sr.PCSCode != 0:
                        if sr.PCSCode not in [5070, 3338, 32161]:
                            msg5 = fail + 'tif raster has unknown or unsupported spatial reference\n'
                            f.write('\tOpen Source Package: ' + msg5)
                        else:
                            msg5 = success + osraster[0] + ' has valid spatial reference\n'
                            f.write('\tOpen Source Package: ' + msg5)
                    elif not sr.GCS.name == 'GCS_WGS_1984':
                        msg5 = fail + osraster[0] + ' has unknown or unsupported spatial reference\n'
                        f.write('\tOpen Source Package: ' + msg5)
                    else:
                        msg5 = success + osraster[0] + ' has valid spatial reference\n'
                        f.write('\tOpen Source Package: ' + msg5)

                    band = os.path.join(dire, osdspatial, osraster[0], 'Band_1')
                    bDepth = arcpy.Describe(band).pixelType
                    if bDepth == 'U32':
                        msg6 = success + osraster[0] + ' has unsigned 32 bit depth \n'
                        f.write('\tOpen Source Package: ' + msg6)
                    else:
                        msg6 = fail + osraster[0] + ' DOES NOT have unsigned 32 bit depth \n'
                        f.write('\tOpen Source Package: ' + msg6)

                    nodata = arcpy.Describe(band).noDataValue
                    if str(nodata) == '2147483647':
                        msg7 = success + osraster[0] + ' has the proper NoData value ' + str(nodata) + '\n'
                        f.write('\tOpen Source Package: ' + msg7)
                    else:
                        msg7 = fail + osraster[0] + ' has an INCORRECT NoData value of: ' + str(nodata) + '\n'
                        f.write('\tOpen Source Package: ' + msg7)



                    # only the right txt tables
                    ostables = os.listdir(osdtabular)
                    if ostables == textTables:
                        msg8 = success + os.path.basename(osp) + ' has the required txt tables \n'
                        f.write('\tOpen Source Package: ' + msg8)

                        # now compare the mukeys
                        df = pd.read_csv(os.path.join(osdtabular, 'mapunit.txt'), sep = '|', names=txtColNames)
                        df['mukey'] = df['mukey'].astype('string')
                        txtkeys = df['mukey'].tolist()
                        txtkeys.sort()

                        with arcpy.da.SearchCursor(os.path.join(osdspatial, osraster[0]), 'MUKEY') as rows:
                            rasterkeys = sorted({row[0] for row in rows})
                        # print(txtkeys)
                        # print(rasterkeys)

                        if txtkeys == rasterkeys:
                            msg9 = success + ' mukeys are identical in  ' + osraster[0] + ' and the mapunit txt file\n'
                            f.write('\tOpen Source Package: ' + msg9)
                        else:
                            msg9 = fail + ' mukeys ARE NOT identical in  ' + osraster[0] + ' and the mapunit txt file\n'
                            f.write('\tOpen Source Package: ' + msg9)

                            unset = set(txtkeys) ^ set(rasterkeys)
                            uncommon = list(unset)
                            uncommon.sort()
                            unmsg = ",".join(map("'{0}'".format, uncommon))

                            msg10 = fail + ' problem mukeys: ' + unmsg + '\n'
                            f.write('\tOpen Source Package: ' + msg10)


                    else:
                        diff = set(ostables) - set(textTables)
                        msg6 = fail + os.path.basename(osp) + ' is missing or has extraneous txt table: '+ str(diff) + '\n'
                        f.write('\tOpen Source Package: ' + msg6)

            # ==============================================================================================================
            msg11='\n'
            esridir = dire + os.sep + 'RSS_' + state + ".gdb"
            if not arcpy.Exists(esridir):
                msg12 = fail + 'ESRI geodatabase not located\n'
                f.write('\tESRI GDB: ' + msg12)
            else:
                arcpy.env.workspace = esridir

                esriraster = arcpy.ListRasters()

                if len(esriraster) != 1:
                    msg13 = fail + 'unable to find a MapunitRaster_10m'
                    f.write('\tESRI GDB: ' + msg13)
                elif not esriraster[0].startswith('MapunitRaster_10m'):
                    msg13 = fail + 'unable to locate the MapunitRaster_10m\n'
                    f.write('\tESRI GDB: ' + msg13)
                elif esriraster[0].count("_") != 3:
                    msg13 = fail + 'unable to locate a properly identified MapunitRaster_10m_date-stamp tif raster\n'
                    f.write('\tESRI GDB: ' + msg13)
                else:
                    try:
                        i = esriraster[0].rfind("_")
                        stamp = esriraster[0][i + 1:i + 7]
                        int(stamp)
                        msg13 = success + 'located properly named tif raster ' + esriraster[0] + '\n'
                        f.write('\tESRI GDB: ' + msg13)
                    except:
                        msg13 = fail + 'unable validate date stamp\n'
                        f.write('\tESRI GDB: ' + msg13)
                        # metadata

                    # meta = [f for f in osrfiles if f.endswith('.tif.xml')]
                    # if len(meta) == 0:
                    #     msg4 = fail + 'unable to locate a xml metadata file\n'
                    #     f.write('\tESRI GDB: ' + msg4)
                    # else:
                    #     msg4 = success + 'found a .tif.xml metadata file\n'
                    #     f.write('\tESRI GDB: ' + msg4)


                murasdesc = arcpy.Describe(esriraster[0])
                murassr = murasdesc.spatialReference
                if murassr.PCSCode != 0:
                    if murassr.PCSCode not in [5070, 3338, 32161]:
                        msg15 = fail + 'gdb raster has unknown or unsupported spatial reference\n'
                        f.write('\tESRI GDB: ' + msg15)
                    else:
                        msg15 = success + esriraster[0] + ' has valid spatial reference\n'
                        f.write('\tESRI GDB: ' + msg15)
                elif not murassr.GCS.name == 'GCS_WGS_1984':
                    msg15 = fail + esriraster[0] + ' has unknown or unsupported spatial reference\n'
                    f.write('\tESRI GDB: ' + msg15)
                else:
                    msg15 = success + esriraster[0] + ' has valid spatial reference\n'
                    f.write('\tESRI GDB: ' + msg15)

                esriband = os.path.join(esriraster[0], 'Band_1')
                esriDepth = arcpy.Describe(esriband).pixelType
                if esriDepth == 'U32':
                    msg16 = success + esriraster[0] + ' has unsigned 32 bit depth \n'
                    f.write('\tESRI GDB: ' + msg16)
                else:
                    msg16 = fail + esriraster[0] + ' DOES NOT have unsigned 32 bit depth \n'
                    f.write('\tESRI GDB: ' + msg16)

                # nodata = arcpy.Describe(band).noDataValue
                # if str(nodata) == '2147483647':
                #     msg7 = success + osraster[0] + ' has the proper NoData value ' + str(nodata) + '\n'
                #     f.write('\tESRI GDB: ' + msg7)
                # else:
                #     msg7 = fail + osraster[0] + ' has an INCORRECT NoData value of: ' + str(nodata) + '\n'
                #     f.write('\tESRI GDB: ' + msg7)

                # only the right txt tables
                esritables = arcpy.ListTables()
                esritables.sort()
                # print(esritables)

                if esritables == gdbTables:
                    msg18 = success + arcpy.env.workspace + ' has the required gdb tables \n'
                    f.write('\tESRI GDB: ' + msg18)

                    # now compare the mukeys
                    # df = pd.read_csv(os.path.join(osdtabular, 'mapunit.txt'), sep='|', names=txtColNames)
                    # df['mukey'] = df['mukey'].astype('string')
                    # txtkeys = df['mukey'].tolist()
                    # txtkeys.sort()

                    with arcpy.da.SearchCursor('mapunit', 'mukey') as rows:
                        gdbkeys = sorted({row[0] for row in rows})

                    with arcpy.da.SearchCursor(esriraster[0], 'MUKEY') as rows:
                        esrirasterkeys = sorted({row[0] for row in rows})
                    # print(txtkeys)
                    # print(rasterkeys)

                    if gdbkeys == esrirasterkeys:
                        msg20 = success + 'mukeys are identical in  ' + esriraster[0] + ' and the mapunit gdb table\n'
                        f.write('\tESRI GDB: ' + msg20)
                    else:
                        msg20 = fail + 'mukeys ARE NOT identical in  ' + esriraster[0] + ' and the mapunit gdb table\n'
                        f.write('\tESRI GDB: ' + msg20)

                        gdbunset = set(gdbkeys) ^ set(esrirasterkeys)
                        gdbuncommon = list(gdbunset)
                        gdbuncommon.sort()
                        gdbunmsg = ",".join(map("'{0}'".format, gdbuncommon))

                        msg21 = fail + ' problem mukeys: ' + gdbunmsg + '\n'
                        f.write('\tESRI GDB: ' + msg21)

                else:
                    diff = set(esritables) ^ set(gdbTables)
                    # print(diff)
                    msg18 = fail + arcpy.env.workspace + ' is missing or has extraneous tables.  FIX and RERUN tool.\n'
                    f.write('\tESRI GDB: ' + msg18)

                    untbls = list(diff)
                    untbls.sort()
                    untblsmsg = ",".join(map("'{0}'".format, untbls))
                    msg19 = fail + 'Problem gdb tables ' + untblsmsg + '\n'
                    f.write('\tESRI GDB: ' + msg19)

        f.write('\n')


import os, arcpy
from datetime import datetime
import pandas as pd

user = os.environ.get('USERNAME')
now = datetime.now()
now_str = now.strftime("%d/%m/%Y %H:%M:%S")
fail = 'HARD FAIL- '
success = 'SUCCESS- '
textTables = ['ccancov.txt', 'ccrpyd.txt', 'cdfeat.txt', 'cecoclas.txt', 'ceplants.txt', 'cerosnac.txt', 'cfprod.txt',
          'cfprodo.txt', 'cgeomord.txt', 'chaashto.txt', 'chconsis.txt', 'chdsuffx.txt', 'chfrags.txt', 'chorizon.txt',
          'chpores.txt', 'chstr.txt', 'chstrgrp.txt', 'chtexgrp.txt', 'chtexmod.txt', 'chtext.txt', 'chtextur.txt',
          'chunifie.txt', 'chydcrit.txt', 'cinterp.txt', 'cmonth.txt', 'comp.txt', 'cpmat.txt', 'cpmatgrp.txt',
          'cpwndbrk.txt', 'crstrcts.txt', 'csfrags.txt', 'csmoist.txt', 'csmorgc.txt', 'csmorhpp.txt', 'csmormr.txt',
          'csmorss.txt', 'cstemp.txt', 'ctext.txt', 'ctreestm.txt', 'ctxfmmin.txt', 'ctxfmoth.txt', 'ctxmoicl.txt',
          'distimd.txt', 'distlmd.txt', 'distmd.txt', 'lareao.txt', 'legend.txt', 'ltext.txt', 'mapunit.txt',
          'msdomdet.txt', 'msdommas.txt', 'msidxdet.txt', 'msidxmas.txt', 'msrsdet.txt', 'msrsmas.txt', 'mstab.txt',
          'mstabcol.txt', 'muaggatt.txt', 'muareao.txt', 'mucrpyd.txt', 'mutext.txt', 'README.txt', 'sacatlog.txt',
          'sainterp.txt', 'sdvalgorithm.txt', 'sdvattribute.txt', 'sdvfolder.txt', 'sdvfolderattribute.txt',
          'version.txt']

gdbTables = ['chaashto', 'chconsistence', 'chdesgnsuffix', 'chfrags', 'chorizon', 'chpores', 'chstruct', 'chstructgrp',
             'chtext', 'chtexture', 'chtexturegrp', 'chtexturemod', 'chunified', 'cocanopycover', 'cocropyld',
             'codiagfeatures', 'coecoclass', 'coeplants', 'coerosionacc', 'coforprod', 'coforprodo', 'cogeomordesc',
             'cohydriccriteria', 'cointerp', 'comonth', 'component', 'copm', 'copmgrp', 'copwindbreak', 'corestrictions',
             'cosoilmoist', 'cosoiltemp', 'cosurffrags', 'cosurfmorphgc', 'cosurfmorphhpp', 'cosurfmorphmr',
             'cosurfmorphss', 'cotaxfmmin', 'cotaxmoistcl', 'cotext', 'cotreestomng',
             'cotxfmother', 'distinterpmd', 'distlegendmd', 'distmd', 'featdesc', 'laoverlap',
             'legend', 'legendtext', 'mapunit', 'mdstatdomdet', 'mdstatdommas', 'mdstatidxdet', 'mdstatidxmas',
             'mdstatrshipdet', 'mdstatrshipmas', 'mdstattabcols', 'mdstattabs', 'month', 'muaggatt', 'muaoverlap',
             'mucropyld', 'mutext', 'sacatalog', 'sainterp', 'sdvalgorithm', 'sdvattribute', 'sdvfolder',
             'sdvfolderattribute']
gdbTables.sort()


txtColNames = ['musym', 'muname', 'mukind', 'mustatus', 'muacres', 'mapunitlfw_l', 'mapunitlfw_r', 'mapunitlfw_h',
               'mapunitpfa_l', 'mapunitpfa_r', 'mapunitpfa_h', 'farmlndcl', 'muhelcl', 'muwathelcl', 'muwndhelcl',
               'interpfocus', 'invesintens', 'iacornsr', 'nhiforsoigrp', 'nhspiagr', 'vtsepticsyscl', 'mucertstat',
               'lkey', 'mukey']

top = arcpy.GetParameterAsText(0)
# top = r'D:\GIS\PROJECT_22\RSS-VALIDATE\EXAMPLE'

os.chdir(top)
checkdir = list()
states = ['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO',
          'CT', 'DC', 'DE', 'FL', 'FM', 'GA', 'GU',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY',
          'LA', 'MA', 'MD', 'ME', 'MH', 'MI', 'MN',
          'MO', 'MP', 'MS', 'MT', 'MX', 'NC', 'ND',
          'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
          'OK', 'OR', 'PA', 'PR', 'PW', 'RI', 'SC',
          'SD', 'TN', 'TX', 'US', 'UT', 'VA', 'VI',
          'VT', 'WA', 'WI', 'WV', 'WY']

with open(os.path.join(top, 'log.log'), 'w') as logf:
    logf.write("User: " + user + "\n")
    logf.write("Time: " + now_str + "\n\n\n")
    dirs = os.listdir(top)
    for d in dirs:
        if os.path.isdir(d) and d in states:
            topstate = d
            seconds = os.listdir(os.path.join(top, d))
            if 'RSS_' + topstate and 'RSS_' + topstate + '.gdb' in seconds:
                # len(seconds) == 2:
                checkdir.append(os.path.join(top, d))

    rssStates = '.'.join(map("{0}".format, [os.path.basename(c) for c in checkdir]))
    msg1 = "The following states have an RSS that will be validated:\n" + rssStates + "\n"
    # arcpy.AddMessage(msg1)
    logf.write(msg1)

    for dire in checkdir:
        arcpy.AddMessage(dire)
        insstatedir(dire=dire, f=logf)

logf.close()