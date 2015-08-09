#!/usr/local/bin/python
import os
import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET
import shutil
import requests
from xml.dom import minidom
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from PIL import Image

base_url   = "http://media-kitlv.nl"
target_url = base_url + "/all-media/indeling/detail/form/advanced/start/51?q_searchfield=tigers"
target_xml = base_url + "/index.php?option=com_memorixbeeld&amp;view=record&amp;format=topviewxml&amp;tstart=0&amp;id="

if not len(sys.argv) > 1:
	raise SystemExit("Usage: %s url" % sys.argv[0])

target_url = sys.argv[1]

#target_url = "http://media-kitlv.nl/all-media/indeling/detail/start/1?q_theme_id=05fc7616-d9f4-4b1b-9d75-97beef243692&titel=vakantie-in-de-bergen"

def getRawfromURL(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	return response.read()

class MyHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.id = ""
	def handle_starttag(self, tag, attrs):
		if (tag == "div"):
			for attr in attrs:
				if (attr[1] == "detailresult"):
					self.id = attrs[1][1][3:]
					
parser = MyHTMLParser()
html   = getRawfromURL(target_url)
parser.feed(html)

target_xml_id_url = target_xml + parser.id

root = ET.fromstring(getRawfromURL(target_xml_id_url))

image_tileurl = root.find('config/tileurl').text

xml_topviews = root.find('topviews')
xml_first_topview = xml_topviews[0]
xml_first_topview_id = xml_first_topview.attrib.get('id')
xml_tjpinfo = xml_first_topview.find('tjpinfo')
xml_layers = xml_tjpinfo.find('layers')
xml_layer_first = xml_layers[-1]

image_width = xml_tjpinfo.find('width').text
image_height = xml_tjpinfo.find('height').text
image_tile_width = xml_tjpinfo.find('tilewidth').text
image_tile_height = xml_tjpinfo.find('tileheight').text


#<layer no="5" starttile="60" cols="14" rows="11" scalefactor="1" width="3330" height="2585"/>

image_tile_starttile = int(xml_layer_first.attrib.get('starttile'))
image_tile_cols 	= int(xml_layer_first.attrib.get('cols'))
image_tile_rows 	= int(xml_layer_first.attrib.get('rows'))
image_tile_width	= int(xml_layer_first.attrib.get('width'))
image_tile_height	= int(xml_layer_first.attrib.get('height'))
image_filepath = xml_tjpinfo.find('filepath').text


image_url_full = image_tileurl + image_filepath

#print image_url_full
#print image_tile_width
#print image_tile_height

def downloadImageTileList(_url, _starttile, _cols, _rows, dir):
	starttile = _starttile;
	cols = _cols;
	rows = _rows;

	if not os.path.exists(dir):
		os.makedirs(dir)
	else:
		print "directory " + dir + "already exist, replacing.."
		
	for row in range(0, rows):
		base =  starttile + (row*cols);
		for col in range(0, cols):
			row_col_tile_url = _url + "&" + str(base+col);
			print "downloading " + row_col_tile_url
			urllib.urlretrieve(row_col_tile_url,dir + "/" + str(base+col) + ".jpg")		

def concatImageTile(_starttile, _cols, _rows,_w, _h, _dir):
			starttile = _starttile
			cols = _cols
			rows = _rows			
			images = []	
	
			result = Image.new("RGBA", (_w, _h))

			#if not os.path.exists(dir):
			#	raise SystemExit("dir not exisr")
				
			#for row in range(0, rows):
			#	base =  starttile + (row*cols);
			#	for col in range(0, cols):
			#		row_col_tile_url =  _dir + "/" + str(base+col) + ".jpg";
			#		#images.append(Image.open(row_col_tile_url))
			#		#urllib.urlretrieve(row_col_tile_url,dir + "/" + str(base+col) + ".jpg")	
			
			y = 0
			x = 0
			cnt = 0	
			last_y = 0;
			
			for i in range(0, rows):
				base =  starttile + (i*cols);
				x = 0								
				for j in range(0, cols):					
					row_col_tile_url =  _dir + "/" + str(base+j) + ".jpg";
					tmp_img = Image.open(row_col_tile_url)					
					result.paste(tmp_img, (x, y))	
					x = x + tmp_img.size[0]	
					last_y = tmp_img.size[1]			
					cnt = cnt + 1
					del tmp_img					
				y = y + last_y
							
			result.save(_dir + "/" + "result.jpg")

print ":: download finished..."
downloadImageTileList(image_url_full, image_tile_starttile, image_tile_cols, image_tile_rows, xml_first_topview_id)
print ":: merge image..."
concatImageTile(image_tile_starttile, image_tile_cols, image_tile_rows,image_tile_width, image_tile_height, xml_first_topview_id)
print ":: merge image...done"

#for child in topviews:
#	print child.attrib.get('id')

#print html