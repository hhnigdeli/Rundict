import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shlex
from bs4 import BeautifulSoup
from math import sin, cos, sqrt, atan2, radians

class route(object):
    def kml_to_df( file_name,tag="LineString",seperator=","):
        """
        to  convert .kml file  to Pandas DataFrame        
        ---------------------------------------------------------------------------------------------
        example,   
        DataFrame = route.kml_to_df(file_name= "file.kml",tag="LineString",seperator=",")
        """
        data=[]
        infile = open(str(file_name),"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        titles = soup.find_all(str(tag))
        for title in titles:
            data.append(title.get_text())


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
            c = df_3.reset_index(drop=True)
        else:
            df_3 = df_2.dropna()    
            df_4 = df_3[~(df_2 == 0).any(axis=1)]
            c = df_4.reset_index(drop=True)
        return c

    def gpx_to_df( file_name):
        """
        to  convert .gpx file  to Pandas DataFrame        
        ---------------------------------------------------------------------------------------------
        example,      
        DataFrame = route.gpx_to_df(file_name= "file.gpx")
        """
        lat=[]
        lon =[]
        att =[]
        elev=[]
                
        infile = open(str(file_name),"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
                        
        with open(str(file_name),"r") as raw_resuls:
            results = BeautifulSoup(raw_resuls, 'lxml')
       
        for element in results.find_all("trkseg"):
            for trkpt in element.find_all("trkpt"):
                lat.append(trkpt['lat'])
                lon.append(trkpt['lon'])
                att.append(re.findall("<ele>(.*?)</ele>", str(trkpt)))
                
        print("Points have been read. Alt:{}, Lat:{}, Long:{}".format(len(att),len(lat),len(lon)))
        mastardata = {"Lat":lat,"Long":lon,"Alt":att }
        mastardf = pd.DataFrame(mastardata)
        b = mastardf.astype({"Lat":"float","Long":"float","Alt":"str"})        
        c = [i[2:][:-2] for i in b.Alt]
        for i in c:
            if i == '':
                elev.append(np.nan)                
            else:
                elev.append(float(i))
        b = b[["Lat","Long"]]
        b["Alt"] = pd.DataFrame(elev)
        b["Alt"] = b["Alt"].interpolate(method='linear', limit_direction='forward',limit=50)

        return  b
    
    def add_distance(data,radius=6371):
        """
        to add distances between two points induvisually and acumulated
        route.add_distance(world_radius=6371, data)
        ---------------------------------------------------------------------------------------------
        radius = default 6371 kms
        data = Pandas DataFrame includes Lat & Long olumns
        ---------------------------------------------------------------------------------------------

        returns,
                Lat       Long        Alt       Dist         Cdist
        0      32.003820  36.538675  -7.100000   0.000000      0.000000
        1      32.003716  36.538640  10.000000  12.029010     12.029010
        2      32.003591  36.538621  10.000000  14.011834     26.040844
        """      
        #to calculate distances between to gps points and aculated distances 
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
    
    def add_Asc(data,AscUpLim,AscLowLim):

        """
        to add Ascent variable to DataFrame 
        AscUpLim = Clear outliars up limit and replace lineer data to it
        AscLowLim = Clear outliars low  limit and replace lineer data to it
        data = pandas Dataframe must include columns,
                 Lat       Long        Alt       Dist         Cdist
        0      32.003820  36.538675  -7.100000   0.000000      0.000000
        1      32.003716  36.538640  10.000000  12.029010     12.029010
        2      32.003591  36.538621  10.000000  14.011834     26.040844
        
        ---------------------------------------------------------------------------------------------
        data_with_ascent = route.add_Asc(data=DataFrame, AscUpLim= 2 , AscLowLim= -2 )
        
        returns,
                Lat 	Long 	    Alt 	        Dist 	    Cdist 	    Asc 	   AscFiltered 	Ascent 	    Descent
        0 	35.097066 	37.858644 	1623.000610 	0.000000 	0.000000 	0.000000 	0.000000 	0.000000 	0.000000
        1 	35.097043 	37.858640 	1624.600586 	2.583244 	2.583244 	1.599976 	1.599976 	1.599976 	0.000000
        2 	35.097021 	37.858636 	1626.200562 	2.473208 	5.056452 	1.599976 	1.599976 	1.599976 	0.000000
        
        """

        Asc = []
        for i in range(len(data)):
            if i == 0:
                Asc.append(0)
            else:
                Ascent = data.Alt[i] - data.Alt[i-1]
                Asc.append(Ascent)
        Asc = pd.DataFrame(Asc)
        data["Asc"] = Asc
        Asc1 = pd.DataFrame(data["Asc"])
        Asc1.loc[Asc1.Asc >  AscUpLim , :] = np.nan
        Asc1.loc[Asc1.Asc < AscLowLim , :] = np.nan
        data["AscFiltered"] = Asc1
        data.AscFiltered = data.AscFiltered.interpolate(method='linear', limit_direction='forward',limit=500)
        Asc2=[]
        for i in data.AscFiltered:
            if i<0:
                Asc2.append(0)
            else:
                Asc2.append(i)         
        Asc3=[]
        for i in data.AscFiltered:
            if i>0:
                Asc3.append(0)
            else:
                Asc3.append(i)       
        data["Ascent"] = pd.DataFrame(Asc2)
        data["Descent"] = pd.DataFrame(Asc3)
        del data['AscFiltered']
        del data['Asc']
        return data 
    
    def  add_Slp(data,UpLim=-45,LowLim=45,Srange=10):
        Cdist = []
        Alt = []
        c=0
        for i in range(len(data)):
            if c == 0:
                a = data.Cdist[i]
                b = data.Alt[i]
                Cdist.append(a)
                Alt.append(b)
                c +=1
            elif c < Srange-1:
                Cdist.append("a")
                Alt.append("b")
                c+=1
            elif c == Srange-1:
                Cdist.append("a")
                Alt.append("b")
                c =0 
        if (len(Cdist)-1)%Srange == 0:
            pass
        else:
            while (len(Cdist)-1)%Srange == 8:
                Cdist.append("a")
                Alt.append("b") 
            Cdist.append(list(data.Cdist)[-1])
            Alt.append(list(data.Alt)[-1])
        extDf = pd.DataFrame({"Cdist":Cdist , "Alt":Alt})
        Cdist_ = []
        Alt_ = []
        for i in range(len(extDf)) :
            if type(extDf.Cdist[i])!= str:
                x = extDf.Cdist[i]
                Cdist_.append(x)
        for i in range(len(extDf)) :
            if type(extDf.Alt[i])!= str:
                x = extDf.Alt[i]
                Alt_.append(x)
        extDf_ = pd.DataFrame({"Cdist_":Cdist_ , "Alt_":Alt_})
        extDf_
        _Cdist_ = []
        _Alt_ =[]
        _Slp_ = []
        for i in range(len(extDf_)):
            if i == 0:
                _Cdist_.append(0)
                _Alt_.append(0)
                _Slp_.append(0)
            else:
                cd = extDf_.Cdist_[i] -  extDf_.Cdist_[i-1]
                al = extDf_.Alt_[i] -  extDf_.Alt_[i-1]
                _Cdist_.append(cd)
                _Alt_.append(al)
                _Slp_.append(100*(al/cd))
        _extDf_ = pd.DataFrame({"_Cdist_":_Cdist_ , "_Alt_":_Alt_ , "_Slp_":_Slp_})
        __Slp__ = []
        for i in _extDf_._Slp_ :
            if LowLim < i < UpLim:
                __Slp__.append(i)
                for j in range(Srange-1):
                    __Slp__.append(i)
            elif i <= LowLim :
                __Slp__.append(LowLim)
                for j in range(Srange-1):
                    __Slp__.append(LowLim)
            elif i >= UpLim :
                __Slp__.append(UpLim)
                for j in range(Srange-1):
                    __Slp__.append(UpLim)
        del __Slp__[:Srange]  
        data["Slp"] = pd.DataFrame(__Slp__)     
        return data
    
    def to_graph(data):      
        plt.xlabel('Distance meters')
        plt.ylabel('Altitue meters')
        plt.title('Route Topo')
        plt.plot(data.Cdist, data.Alt, "r-" )
        return plt.show() 
    
class splinter(object):
  
    def find_peaks( data ,x_axis,  y_axis ,scan=1500, h=7,w=5 ):
            """
            to find peak points on the dataset
            find_peaks( data ,x_axis,  y_axis ,scan=1500, h=7,w=5 )
            ---------------------------------------------------------------------------------------------
            data   = Dataset 
            x_axis = x axis of line plot or index 
            y_axis = data points of y axis 
            ---------------------------------------------------------------------------------------------

            splinter.find_peaks(data, data.Cdist , data.Alt , 1500, 7,5)
            
            returns splited line plot on graph and list of edges' index
            
            """
            l_0 = []
            c = x_axis[len(data)-1] / len(data)
            
            x = int(scan/c)
            for i in range(0,len(data),x):
                l_0.append(i)
            
            b=[]
            for i in range(len(l_0)):
                if i == 0:
                    pass
                else:
                    b.append( max(y_axis[l_0[i-1]:l_0[i]]))
            l_1 =[]
            for i in range(len(b)):
                if i == 0 :
                    if  b[i]>b[i+1]:
                        l_1.append(b[i])
                    else:
                        pass
                elif i == len(b)-1:
                    if b[i]> b[i-1]:
                        l_1.append(b[i])
                    else:
                        pass
                elif b[i-1]<b[i]> b[i+1]:
                    l_1.append(b[i])
            
            peak=[]
            for i in range(len(l_1)):
                if i < len(l_1)/2:
                    peak.append(list(x_axis[y_axis == l_1[i]])[0])
                elif i>=len(l_1)/2:
                    peak.append(list(x_axis[y_axis == l_1[i]])[-1])
            plt.rcParams['figure.figsize']=(h,w)
            plt.plot(x_axis,y_axis)
            for i in range(len(peak)):
                plt.vlines(peak[i],ymin=min(y_axis),ymax=list(y_axis[y_axis == l_1[i]])[0])
            plt.xlabel('Distance meters')
            plt.ylabel('Altitue meters')
            plt.title('Route Topo')
            return plt.show()   
