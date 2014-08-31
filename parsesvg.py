# Parse.py
#
# The purpose of this script is importing an Inkscape .svg (XML) file
# and extract from it an XML file with the following information:
# - item x from left
# - item y from top
# - id given to the object (name atribute)
# This info is parsed for every first level item in each layer, and saved and exported
# to a file named like the layer. There is one layer for each level to export.
# TODO: separate data collection and file writing
# TODO: update HTML part (which is buggy and unchecked)
#
# Usage: parse_svg [inkscape svg] [--to-html|--to-json] [--required-names]
#        [--export-png]

import xml.etree.ElementTree as ET
import sys
import subprocess
import os
from math import floor

# namespaces
svg = "{http://www.w3.org/2000/svg}"
inkscape = "{http://www.inkscape.org/namespaces/inkscape}"

svgname = sys.argv[1]
namerequired = False
exportpng = False
if sys.argv[3] == "--required-names":
    namerequired = True
if sys.argv[4] == "--export-png":
    exportpng = True

xmldoc = ET.parse(svgname)
root = xmldoc.getroot()
# parse width and height to int
# example: '800px' -> 800
svg_w = int(root.attrib.get('width')[:-2]) 
svg_h = int(root.attrib.get('height')[:-2])

if sys.argv[2] == "--to-html":
    for layer in root.findall(svg+'g'):
        layername = layer.attrib.get(inkscape+'label')
        xmlfile = open(layername+'.xml','w')
        xmlfile.write('<scene width="'+str(svg_w)+'" height="'+str(svg_h)+
                      '" name="'+layername+'">\n')

    for item in layer:
        itemid   = item.attrib.get('id')
        itemname = item.attrib.get('name')
        itemactive = item.attrib.get('active')
        itemvisible = item.attrib.get('visible')
        
        print('\n------------------------')
        print('-> LOADING item '+itemid)
        
        if( type(itemname).__name__ == 'NoneType' ):
            sys.exit('\n*** ERROR: Item '+itemid+
                     ' has no defined NAME attribute, aborting...')
        if( type(itemvisible).__name__ == 'NoneType' ):
            print('\n!!! WARNING: Item '+itemid+
                  ' has no defined VISIBLE attribute')
            print('!!! Setting it to 1\n')
            itemvisible = "1"
        if( type(itemactive).__name__ == 'NoneType' ):
            print('\n!!! WARNING: Item '+itemid+
                  ' has no defined ACTIVE attribute')
            print('!!! Setting it to 1\n')
            itemactive = "1"

        filename = layername+"_"+itemname

        itemx = int(float(subprocess.check_output(
            "inkscape --query-id "+itemid+" -X "+svgname, shell=True)))
        itemy = int(float(subprocess.check_output(
            "inkscape --query-id "+itemid+" -Y "+svgname, shell=True)))

        print('-> LOADED '+itemid+': '+filename+', x: '+str(itemx)+', y: '+str(itemy))

        xmlfile.write('<item name="'+itemname+'" x="'+str(itemx)+
                      '" y="'+str(itemy)+'" visible="'+itemvisible+
                      '" active="'+itemactive+'" />\n')

        # export to png
        print('-> EXPORTING item '+itemid+'...\n' )
        os.system("inkscape "+svgname+" --export-id "+itemid+
                  " --export-id-only -e"+filename+".png")

    xmlfile.write('</scene>')
    xmlfile.close()

# ---------------------------------------
# JSON
# ---------------------------------------
else:
    for layer in root.findall(svg+'g'):
        layername = layer.attrib.get(inkscape+'label')
        xmlfile = open(layername+'.json','w')
        xmlfile.write('window.'+layername+' = { "width": "'+str(svg_w)+'", "height": "'+str(svg_h)+
                      '", "name": "'+layername+'", "item": [ \n')
        count = 0
      
        for item in layer:
            count = count+1
            itemid   = item.attrib.get('id')
            itemname = item.attrib.get('name')
            itemactive = item.attrib.get('active')
            itemvisible = item.attrib.get('visible')
            
            print('\n------------------------')
            print('-> LOADING item '+itemid)
            
            if namerequired:
                if( type(itemname).__name__ == 'NoneType' ):
                    sys.exit('\n*** ERROR: Item '+itemid+
                             ' has no defined NAME attribute, aborting...')
            else:
                print('\n!!! WARNING: Item '+itemid+
                      ' has no defined NAME attribute')
                print('!!! Setting it to ""\n')
                itemname = ""
            if( type(itemvisible).__name__ == 'NoneType' ):
                print('\n!!! WARNING: Item '+itemid+
                      ' has no defined VISIBLE attribute')
                print('!!! Setting it to 1\n')
                itemvisible = "1"
            if( type(itemactive).__name__ == 'NoneType' ):
                print('\n!!! WARNING: Item '+itemid+
                      ' has no defined ACTIVE attribute')
                print('!!! Setting it to 1\n')
                itemactive = "1"
                
            filename = layername+"_"+itemname
            
            itemx = int(float(subprocess.check_output(
                "inkscape --query-id "+itemid+" -X "+svgname, shell=True)))
            itemy = int(float(subprocess.check_output(
                "inkscape --query-id "+itemid+" -Y "+svgname, shell=True)))
            itemw = int(float(subprocess.check_output(
                "inkscape --query-id "+itemid+" -W "+svgname, shell=True)))
            itemh = int(float(subprocess.check_output(
                "inkscape --query-id "+itemid+" -H "+svgname, shell=True)))
            
            print('-> LOADED '+itemid+': '+filename+', x: '+str(itemx)+
                  ', y: '+str(itemy),', w: '+str(itemw),', h: '+str(itemh))

            xmlfile.write('{ "name": "'+itemname+
                          '", "x": "'+str(itemx)+
                          '", "y": "'+str(itemy)+
                          '", "width": "'+str(itemw)+
                          '", "height": "'+str(itemh)+
                          '", "visible": "'+itemvisible+
                          '", "active": "'+itemactive+'" }')
            if count != len(layer):
                xmlfile.write(",")
            xmlfile.write("\n")

            # export to png
            if exportpng:
                print('-> EXPORTING item '+itemid+'...\n' )
                os.system("inkscape "+svgname+" --export-id "+itemid+
                          " --export-id-only -e"+filename+".png")

        xmlfile.write('] }')
        xmlfile.close()
