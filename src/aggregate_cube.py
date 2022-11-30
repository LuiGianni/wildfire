import harmonize as hz
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
from shapely.geometry import mapping

# Function to print the descriptive statistics of the dataset
def print_dataset_statistics(ds):
    print("Descriptive statistics of the dataset")
    print('The mean of the dataset is : ', ds.mean().values)
    print('The median of the dataset is : ', ds.median().values)
    print('The standard deviation of the dataset is : ', ds.std().values)
    print('The minimum value of the dataset is : ', ds.min().values)
    print('The maximum value of the dataset is : ', ds.max().values)

# define function to loop over the dataset to fill the new variable

#defining the function to get a period days time selection
def get_lastdays_mean_ds(the_ds, t=0, x=0, y=0, period_size=10, variable='u10'):
    """
    This function returns a the mean value of the selected pixel and the selected period of time
    input:
        the_ds: the dataset
        t: the time index
        x: the x index
        y: the y index
        period_size: the size of the period
        variable: the variable to be selected
    output:
        the mean value over the previous period_size days
        of the selected pixel and the selected period of time
    """

    mean_value = the_ds[variable].isel(x=x, y=y, time=slice(t-period_size-1, t-1)).mean(dim='time').values

    return mean_value

def fill_ds_mean(the_ds, period_size=10, list_variables=[]):
    """
    This function appends and fills the new variables of the dataset with the mean values,
    then drops the old ones.
    input:
        the_ds: the dataset
        period_size: the size of the period
        list_variables: the variables to be selected
    output:
        the dataset with the new variables filled
    """
    # Add a new variable to the dataset
    for var in list_variables:
        the_ds[var + '_last' + str(period_size) + 'days' + '_mean'] = (('x', 'y',
                                                                        'time'), np.zeros(
            (the_ds.x.size, the_ds.y.size, the_ds.time.size)))

    # loop over the dataset to fill the new variable
    for var in list_variables:
        for x in range(the_ds.x.size):
            for y in range(the_ds.y.size):
                for t in range(the_ds.time.size):
                    the_ds[var + '_last' + str(period_size) + 'days' + '_mean'].values[x, y,
                                                                                       t] = get_lastdays_mean_ds(the_ds,
                                                                                                                 t=t,
                                                                                                                 x=x,
                                                                                                                 y=y,
                                                                                                                 period_size=period_size,
                                                                                                                 variable=var)

    # drop the old variables
    the_ds = the_ds.drop(dynamic_variables)

    return the_ds


if __name__ == "__main__":
    # Create a path to the data directory
    path_data = "../data/final/"

    # Load the data set
    ds = xr.open_dataset(path_data + 'final_datacube_gps.nc')

    # Create a list of dynamic variables
    dynamic_variables = ['ET_500m',
                         'Fpar_500m',
                         'u10',
                         'v10',
                         't2m',
                         'tp',
                         'LST_Day_1km',
                         'LST_Night_1km',
                         '_1_km_16_days_EVI']

    # Adding aggregated variables with fill_ds_mean function
    #ds = fill_ds_mean(ds, period_size=1, list_variables=dynamic_variables)

    # Create a column t2m_mean which is the mean of t2m over the last 10 days before the current day with rolling function
    #ds['t2m_mean'] = ds.t2m.rolling(time=10, center=False).mean()

    # Do the sae for all dynamic variables
    for var in dynamic_variables:
        ds[var + '_mean'] = ds[var].rolling(time=10, center=False).mean()

    # put this for loop into a function
    def aggregate_dataset(ds, dynamic_variables, period_size=10):
        """
        This function appends and fills the new variables of the dataset with the mean values,
        then drops the old ones.
        input:
            the_ds: the dataset
            period_size: the size of the period
            list_variables: the variables to be selected
        output:
            the dataset with the new variables filled
        """
        # Add a new variable to the dataset
        for var in dynamic_variables:
            ds[var + '_mean'] = ds[var].rolling(time=period_size, center=False).mean().dropna(dim='time')

        return ds


    # Check content of the xarray dataset
    print(ds)




    #ds['t2m_mean'] = ds.t2m.rolling(time=10, center=True).mean()

    # plot this new variable
    ds.t2m_mean.isel(time=100).plot()

    # Describe this new variable
    print_dataset_statistics(ds.t2m_mean)

    #PLot the distribution of the variable t2m_mean and t2m
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ds.t2m_mean.isel(time=50).plot.hist(ax=ax[0])
    ds.t2m.isel(time=50).plot.hist(ax=ax[1])
    ax[0].set_title('t2m_mean')
    ax[1].set_title('t2m')
    plt.show()


