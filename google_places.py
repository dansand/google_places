
# coding: utf-8

# ## Get places using google maps

# In[2]:

import googlemaps
import numpy as np


# In[25]:

#Open a google maps client

YourApiKey = 'AIzaSy...' #provide your API key here

gm = googlemaps.Client(YourApiKey)


# In[3]:

#Test the places_nearby function

#places  = gm.places_nearby(keyword=None, location=(-37.80, 144.948), radius=300)
#places


# In[6]:

## Create a grid in Lat Lon space


def meters_to_lat(meters):
    """
    Convert meters to a crude latitude-longitude measure, 
    using the unit longitude distance at the equator
    """
    return meters/111.2e3

def create_grids(ulLatLon, lrLatLon, meters_spacing = 400., shape=()):
    """
    This function creates a set of cells defined by a rectangle, and spacing in meters.
    It return the coordinates of the cell centers - 
        which are the points where we conduct our places_nearby() searches
        
    Note that the overall cell soze will be slightly smaller meters_spacing paramter, 
    as I use : nx = int(np.ceil((lrLatLon[1] - ulLatLon[1])/lldist))
               xs = np.linspace(ulLatLon[1], lrLatLon[1], nx)
    Alternatively a shape tuple can be provide, eg (3, 5) defining the size of the grid. 
 
    
    """
    if not shape:
        lldist = meters_to_lat(meters_spacing)
        nx = int(np.ceil((lrLatLon[1] - ulLatLon[1])/lldist))
        ny = int(abs(np.ceil((lrLatLon[0] - ulLatLon[0])/lldist)))
        xs = np.linspace(ulLatLon[1], lrLatLon[1], nx)
        ys =  np.linspace(ulLatLon[0], lrLatLon[0], ny)
    else:
        lldist = meters_to_lat(meters_spacing)
        xs = np.linspace(ulLatLon[1], lrLatLon[1], shape[0])
        ys =  np.linspace(ulLatLon[0], lrLatLon[0], shape[1])
    X, Y = np.meshgrid(xs , ys) #Thes are coordinates of the cell vertices
    subX, subY = np.copy(X), np.copy(Y)
    subX = subX[:-1, :-1] + lldist/2. #These give the points at the centre of the cells
    subY = subY[:-1, :-1] + lldist/2.
    return subX, subY


# In[7]:

#Test the create gride function
X, Y = create_grids((-37.805, 144.947), (-37.820, 144.970), meters_spacing = 400., shape=())
X1, Y1 = create_grids((-37.805, 144.947), (-37.820, 144.970), meters_spacing = False, shape=(14,8))


# In[8]:




# In[16]:

##########
#In this block we search through a grid and extract records cel-by-cell. 
#If the records query in anny cell maxes out (i.e. hits 20 record), 
#we create a finer grid and search again
##########

ULCRN = (-37.805, 144.947) #Approx melbourne CBD limits
LRCRN = (-37.820, 144.970)

spacing = 400. #intial spacing of cells in our grid
X, Y = create_grids(ULCRN, LRCRN, meters_spacing = spacing, shape=()) #create grids
orig_shape = Y.shape
max_levels = 2. #this paramter will limit the number of refinement levels 
lengths = [21]  #A dummy parameter, ultimately we try to reduce this below 20, meaning we have 
                #will have returned all results for each searhc area
fac = 1.        #This is the scaling factor for our grid cell size and search radius


while max(lengths) >= 20 and fac <= max_levels: 
    print('##Iteration at grid level: ' + str(int(fac)))
    new_shape = tuple(np.array(orig_shape)*fac)
    new_spacing = spacing/fac
    print('##Search radius in meters: ' + str(new_spacing))
    records = []
    lengths = []
    X, Y = create_grids((-37.805, 144.947), (-37.820, 144.970), meters_spacing = new_spacing, shape=new_shape)
    #print(X.shape)
    for index, value in np.ndenumerate(X): #loop through cells of current grid
        #print index,
        y = Y[index]
        x = X[index]
        #print(x,y, new_spacing)
        places  = gm.places_nearby(keyword='restaurant', location=(y,x), radius=new_spacing )
        records.append(places['results'])
        #print(len(places['results']))
        lengths.append(len(places['results'])) 
        
    fac *= 2 #Increase the grid refinment factor
print('##finished')
    


# In[11]:

#records


# In[12]:

y,x


# ### Parse data with Pandas

# In[13]:

import pandas as pd


# In[ ]:




# In[17]:

df = pd.DataFrame(columns=['name', 'lat', 'lon', 'rating'])
for cell in records:
    for place in cell:
        #print(place)
        name = place['name']
        lat = place['geometry']['location']['lat']
        lon = place['geometry']['location']['lng']
        try:
            rating = place['rating'] #Not all places have ratings, so use try - except
        except:
            rating = ''
        series = pd.Series([name, lat, lon, rating], index=['name', 'lat', 'lon', 'rating'])
        df = df.append(series,  ignore_index=True)
print(name, lat, lon, rating)


# In[24]:

#Take a quick look at our data frame
df.head()


# In[22]:

#Drop duplicates
df2 = df.drop_duplicates('name')
df2.shape


# In[ ]:

#output to csv
#df2.to_csv('results.csv')


# ## Next steps
# 
# It would be nice to make use of numpy masked arrays so we only refine our search in locations where necessary. This would lead to much faster search results.

# In[ ]:



