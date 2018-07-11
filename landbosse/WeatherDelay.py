"""
WeatherDelay.py
Created by Annika Eberle and Owen Roberts on Apr. 3, 2018

Calculates weather delays for a project based on weather data, season of construction, operational hours, mission time,
and critical wind speed -- only calculates wind delays right now

Get weather data
Get season dictionary
Get season of operation
Get operation construction time
Get start delay from beginning of weather window
Get mission time for operation
Get critical wind speed

Create weather window based on weather data, season dictionary, season of construction, and operation construction time

Calculate wind delay based on weather window, operation start delay, mission time, and critical wind speed

"""
import numpy as np
import pandas as pd


def create_weather_window(weather_data, season_id, season_construct, time_construct):
    """
    Creates weather window based on season of construction and time of construction (i.e., normal vs. long hours).

    :param weather_data: data frame with weather data of interest (only accomodates single year of data right now)
    :param season_id: dictionary that maps seasons to months
    :param season_construct: list of seasons for construction (e.g., ['spring', 'summer'])
    :param time_construct: string that describes operational time (e.g., normal vs. long hours)
    :return: weather_window: filtered weather window containing data specific to season and time of construction
    """

    # set column names for weather data
    column_names = weather_data[4:].columns
    weather_data = weather_data[4:].rename(columns={column_names[0]: 'Date',
                                                    column_names[1]: 'Temp C',
                                                    column_names[2]: 'Pressure atm',
                                                    column_names[3]: 'Direction deg',
                                                    column_names[4]: 'Speed m per s'})
    weather_data = weather_data.reset_index(drop=True)

    # extract time data from string in weather file
    print('Extracting time data from weather file...')
    weather_data['Year'] = pd.to_datetime(weather_data['Date']).dt.year
    weather_data['Month'] = pd.to_datetime(weather_data['Date']).dt.month
    weather_data['Day'] = pd.to_datetime(weather_data['Date']).dt.day
    weather_data['Hour'] = pd.to_datetime(weather_data['Date']).dt.hour + 6

    # change speed to numeric value
    weather_data['Speed m per s'] = pd.to_numeric(weather_data['Speed m per s'])

    # create time window for normal (8am to 6pm) versus long (24 hour) time window for operation
    print('Creating weather window...')
    weather_data['Time window'] = weather_data['Hour'].between(8, 18, inclusive=True)
    boolean_dictionary = {True: 'normal', False: 'long'}
    weather_data['Time window'] = weather_data['Time window'].map(boolean_dictionary)

    # get list of months of interest based on seasons of construction (needed for > 1 seasons)
    month_list = list()
    for season in season_construct:
        for month in season_id[season]:
            month_list.append(month)

    # select data in weather window of interest
    weather_window = weather_data.where((weather_data['Time window'] == time_construct) &
                                        (weather_data['Month'].isin(month_list))).dropna(thresh=1)
    weather_window = weather_window.reset_index(drop=True)

    return weather_window


def calculate_wind_delay(weather_window, start_delay, mission_time, critical_wind_speed, height_interest, wind_shear_exponent):
    """
    Calculates wind delay based on weather window, mission time, and critical wind speed.

    :param weather_window: filtered weather window containing data specific to season and time of construction
    :param start_delay: delay of mission from start of weather window
    :param mission_time: length of mission (i.e., time that it takes to complete operation) in hours
    :param critical_wind_speed: wind speed at which operation must be shutdown
    :return: list containing the number of hours for each wind delay encountered during mission
             count of list = number of weather delays; value in list = duration of weather delay)
    """

    # print('Calculating wind delay')
    # select only weather data after start delay (e.g., delay due to need for waiting on prior operation before start)
    weather_data = weather_window[weather_window.index > start_delay]
    mission_end = weather_window.index[weather_window.index == start_delay][0] + mission_time

    # check if mission time exceeds size of weather window
    if mission_end > len(weather_window.index):
        print('Warning: Mission time larger than weather window')

    # set mission weather to time window of interest and reset indices for data frame
    mission_weather = weather_data[weather_data.index <= mission_end].reset_index(drop=True)

    # create new column for boolean for weather delay (true or false) based on critical wind speed
    # todo: might want to modify to consider other types of weather delays (e.g., rain, lightening)
    mission_weather['Wind delay'] = mission_weather['Speed m per s'] * (height_interest / 100) ** (wind_shear_exponent) > critical_wind_speed

    if mission_weather['Wind delay'].any() == True:
        # create new weather delay data frame and determine number of hours of delay along with boolean for > 1 hr
        weather_delay = pd.DataFrame()
        weather_delay['Hour delay diff'] = (mission_weather['Hour'][mission_weather['Wind delay'] == True].diff())
        weather_delay['Hour delay bool'] = (weather_delay['Hour delay diff'] == 1)
        weather_delay = weather_delay.reset_index(drop=True)

        # fix value that got removed due to differencing
        # because selecting values that == 1 then if hour delay diff [1] == 1, hour delay bool should be true
        # otherwise remains false
        if len(weather_delay['Hour delay diff']) > 1:
            if weather_delay['Hour delay diff'][1] == 1:
                weather_delay.loc[weather_delay.index == 0, 'Hour delay bool'] = True

        # add extra row at end of data frame to make sure the last data point is counted
        extra_row = pd.DataFrame([['NaN', ~(weather_delay.iloc[-1]['Hour delay bool'])]], columns=['Hour delay diff', 'Hour delay bool'])
        weather_delay = weather_delay.append(extra_row)

        # check whether the weather delay is consecutive or not based on hour delay bool
        # (false then only 1 hr delay; otherwise consecutive)
        index_change = np.flatnonzero(np.diff(np.r_[0, weather_delay['Hour delay bool'], 0]))

        # find which indices to include based on delay boolean for cases where the indices change
        # (only include cases where delay is greater than 1 hr)
        include_change = weather_delay['Hour delay bool'].where(weather_delay.index.isin(index_change))
        include_change = include_change.dropna()  # drops NaNs
        include_change = (include_change == 1).reset_index(drop=True)  # resets indices
        if len(include_change) != 0:
            include_change.iloc[-1] = ~(include_change.iloc[-1])  # removes last value that was added to pad data from diff

            # calculate the number of hours for each consecutive delay > 1 hr
            if weather_delay.iloc[-2]['Hour delay bool'] == True:
                greater_than_1hr = np.diff(index_change)[include_change[0:len(np.diff(index_change))]]

            else:
                greater_than_1hr = np.diff(index_change)[include_change[0:len(np.diff(index_change))+1]]

        else:
            greater_than_1hr = []

        # calculate the number of single hour delays
        count_1hr = weather_delay['Hour delay bool'].where(weather_delay['Hour delay bool'] == False).count()

        # create list of weather delays including > 1 hr and 1 hr delays
        delay_duration = list(greater_than_1hr) + list(np.ones(count_1hr))
    else:
        delay_duration = list([0])

    delay_duration = delay_duration
    return delay_duration