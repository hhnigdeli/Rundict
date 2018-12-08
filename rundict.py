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
    
    def to_df(data, seperator=","):
        """
        to  convert file that has been read before to Pandas DataFareme
        
        to_df(data) 

        example,

        from rundict import gpsdata
        a = gpsdata.read(file_name= file.kml)
        DataFrame = gpsdata.to_df(data=a)

        """
        df_s =[]
        for i in range(len(data)):
            a = shlex.split(data[i], posix=False)
            df_s.append(a)
        df = pd.DataFrame(df_s).transpose()
        df.columns =["data"]
        df[['Lat', 'Long', 'Alt']] = df.data.str.split(seperator,expand=True)
        df = df[['Lat', 'Long', 'Alt']].astype({"Lat": float , "Long": float,"Alt":float})
        return df
