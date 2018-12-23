import pandas as pd
import matplotlib.pyplot as plt
import shlex
from bs4 import BeautifulSoup
from math import sin, cos, sqrt, atan2, radians

class route(object):

    def read(file_name,tag="LineString"):
        """
        to read .kml file
        read_kml(file_name="file.kml",tag="coordinates")
        ----------------------------------------------------------------------------------------------
        file_name = .xml or .kml file in the directory
        tag = The tag name that includes Lat, Long and Altitute data most probably it is "coordinates"
        """
        coor=[]
        infile = open(str(file_name),"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        titles = soup.find_all(str(tag))
        for title in titles:
            coor.append(title.get_text()) 
        return coor
    
    def to_df( data, seperator=","):
        """
        to  convert file that has been read before to Pandas DataFareme
        to_df(data) 
        ---------------------------------------------------------------------------------------------
        example,
        from rundict import gpsdata
        a = gpsdata.read(file_name= "file.kml")
        DataFrame = gpsdata.to_df(data=a)
        """
        #to split merged text values by " "
        liste_0 =[]
        for i in range(len(data)):
            a = shlex.split(data[i], posix=False)
            liste_0.append(a) 
        df_0 = pd.DataFrame(liste_0).transpose()
        #to merge different columns that represent continious gpsdata to one column
        liste_1 = []
        for i in range(len(df_0.columns)):
            liste_1.append(df_0[i])
        d = pd.concat(liste_1, ignore_index=True)
        df_1=pd.DataFrame(d)
        #to split one column values three columns represent Lat Long and Alt 
        df_1.columns = ["column"]
        df_1[['Lat', 'Long', 'Alt']] = df_1.column.str.split(seperator,expand=True)
        df_2 = df_1[['Lat', 'Long', 'Alt']].astype({"Lat": float , "Long": float,"Alt":float})
        counter = 0
        if df_2.Alt.sum() < 15:
            df_3 = df_2.dropna()
            df_4 = df_3.reset_index(drop=True)
        else:
            df_3 = df_2.dropna()    
            df_4 = df_3[~(df_2 == 0).any(axis=1)]
            df_4 = df_4.reset_index(drop=True)
        return df_4

    def add_distance(data,radius=6371):
        """
        to add distances between two points induvisually and acumulated
        add_distance(world_radius=6371, data)
        ---------------------------------------------------------------------------------------------
        radius = default 6371 kms
        data = Pandas DataFrame includes Lat & Long olumns
        ---------------------------------------------------------------------------------------------
        example,
        from rundict import gpsdata
        a = gpsdata.read(file_name= "file.kml")
        DataFrame = gpsdata.to_df(data=a)
        data_with_dists = gpsdata.add_distance(data=DataFrame, radius=6371 )

        returns,
                Lat       Long        Alt       Dist         Cdist
        0      32.003820  36.538675  -7.100000   0.000000      0.000000
        1      32.003716  36.538640  10.000000  12.029010     12.029010
        2      32.003591  36.538621  10.000000  14.011834     26.040844
        """      
        #to colculate distances between to gps points and aculated distances 
        distances = []
        for i in range(len(data)):
            if i == 0:
                distances.append(0)
            else:
                lat1 = radians(data.Lat[i])
                lon1 = radians(data.Long[i])
                lat2 = radians(data.Lat[i-1])
                lon2 = radians(data.Long[i-1])
                dlon = lon1 - lon2
                dlat = lat1 - lat2
        #to calculate distace between two points on the earth
                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = radius * c
                distances.append(distance*1000)
        distances = pd.DataFrame(distances)
        c_distances = distances.cumsum()
        distances.columns = ["Dist"]
        c_distances.columns = ["Cdist"]
        dframe=pd.concat([data, distances,c_distances], axis=1)
        return dframe

    def to_graph(data):      
        plt.xlabel('Distance meters')
        plt.ylabel('Altitue meters')
        plt.title('Route Topo')
        plt.plot(data.Cdist, data.Alt, "r-" )
        return plt.show() 
    
    def find_peaks(data,scan=500):

        """
        find_peaks(data,scan=500)

        data = Dataframe that created before from .kml file wit distances
        scan = sacaning range in metres to find peaks in the topo 

        returns peak indicated graph
        
        """

        l_0 = []
        c = data.Cdist[len(data)-1] / len(data)
        scan = 500
        x = int(scan/c)
        for i in range(0,len(data),x):
            l_0.append(i)
        
        b=[]
        for i in range(len(l_0)):
            if i == 0:
                pass
            else:
                b.append( max(data.Alt[l_0[i-1]:l_0[i]]))
        
        l_1 =[]
        for i in range(len(b)):
            if i == 0 :
                if  b[i]>b[i+1]:
                    l_1.append(b[i])
            elif i == len(b)-1:
                if b[i]> b[i-1]:
                    l_1.append(b[i])
            elif b[i-1]<b[i]> b[i+1]:
                l_1.append(b[i])

        l_2=[]
        for i in range(len(l_1)):
            if i == 0 :
                if  l_1[i]>l_1[i+1]:
                    l_2.append(l_1[i])
            elif i == len(l_1)-1:
                if l_1[i]> l_1[i-1]:
                    l_2.append(l_1[i])
            elif l_1[i-1]<l_1[i]> l_1[i+1]:
                l_2.append(l_1[i])

        peak=[]

        for i in range(len(l_2)):

            peak.append(data.index[data['Alt'] == l_2[i]].tolist())

        plt.rcParams['figure.figsize']=(10,3)
        plt.plot(data.Alt)
        for i in range(len(peak)):
            plt.vlines(peak[i][0],min(data.Alt),max(data.Alt),colors="g")
            plt.vlines(peak[i][-1],min(data.Alt),max(data.Alt),colors="r")
        
        return plt.show()
