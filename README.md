<h1>Rundict</h1>

For reading .xml and .kml GPS running route data files and create topo and split the topo by peak points.



first,

from rundict import gpsdata

<h2>Function1, gpsdata.read()</h2>

read(file_name,tag="LineString"):


        """
        to read .kml file
        read_kml(file,tag="coordinates")

        file_name = .xml or .kml file in the directory
        tag = The tag name that includes Lat, Long and Altitute data most probably it is "coordinates"

        """

<h2>Function2, gpsdata.to_df()</h2>

to_df( data, seperator=","):

        """
        to  convert file that has been read before to Pandas DataFareme
        
        to_df(data) 

        example,

        from rundict import gpsdata
        a = gpsdata.read(file_name= "file.kml")
        DataFrame = gpsdata.to_df(data=a)

        """
       
<h2>Function3, gpsdata.add_distance()</h2>

add_distance(data,radius=6371):

        """
        to add distances between two points induvidually and accumulated

        add_distance(world_radius=6371, data)
        
        radius ==> default 6371 kms

        data ==> Pandas DataFrame includes Lat & Long olumns

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
        
<h2>Function4, gpsdata.find_peaks()</h2>

find_peaks(data,scan=500):


        """
        

        data = Dataframe that created before from .kml file wit distances
        scan = scaning range in metres to find peaks in the topo 

        returns peak indicated graph
        
        """
