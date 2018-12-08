import pandas as pd
import shlex
from bs4 import BeautifulSoup

class gpsdata(object):

    def read(file_name,tag="coordinates"):
        """
        to read .kml file
        read_kml(file,tag="coordinates")

        file_name ==> .xml or .kml file in the directory
        tag ==> The tag name that includes Lat, Long and Altitute data most probably it is "coordinates"

        """
        coor=[]
        infile = open(str(file_name),"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        titles = soup.find_all(str(tag))
        for title in titles:
            coor.append(title.get_text())
        
        return coor
