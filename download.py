import datetime

from utilities.utils import generate_dates, download_ionex, date_to_ionex_name, download_sp3_v2, download_clk, ION_root, \
    SP3_root, CLK_root, RNX_root, download_rinex
import numpy as np
import glob
import os
import pickle


def download_ION_SP3_CLK(agency, file_type, dates_sets):
    _names = [date_to_ionex_name(d, agency)[0] for w in dates_sets for d in w]
    _in_folder = glob.glob("./{}/*i".format(file_type))
    _in_folder = [n.split("/")[-1] for n in _in_folder]
    max_retries = 1

    while len(set(_names) - set(_in_folder)) > 0 and max_retries > 0:
        for i in range(len(dates_sets)):

            seq = dates_sets[i]

            try:
                if file_type == ION_root:
                    print(agency, file_type)
                    download_ionex(seq)
                elif file_type == SP3_root:
                    print(agency, file_type)
                    download_sp3_v2(seq)
                elif file_type == CLK_root:
                    print(agency, file_type)
                    download_clk(seq)
            except:
                i -= 1
        max_retries -= 1


def download_RNX(stations, dates_sets):
    for station in stations:
        for seq in dates_sets:
            # print(seq)
            download_rinex(station, seq)


if __name__ == '__main__':

    dates_set_file_path = os.path.join('dates_set_single.pk')
    stations_file_path = os.path.join('stations_single.pk')
    agencies_file_path = os.path.join('agencies.pk')

    # AGENCIES
    if os.path.isfile(agencies_file_path):
        agencies = pickle.load(open(agencies_file_path, 'rb'))
    else:
        agencies = ['c1p', 'igs', 'ckm']
        pickle.dump(agencies, open(agencies_file_path, 'wb'))

    # STATIONS
    if os.path.isfile(stations_file_path):
        stations = pickle.load(open(stations_file_path, 'rb'))
    else:
        stations = ['ramo']  # , 'drag', 'aruc', 'kitg', 'krs1', 'bhr3', 'bhr4', 'tehn', 'hamd']
        # stations = ['alx2','phlw','tays','rash','haly','elat','nrif','petah','spir','ramo','nizn','yrcm','dsea',
        # 'muta','drag','alon','jslm','ammn','hugs','tela','mrav','just','csar','kabr','katz','hram','udmc','laug',
        # 'hrrn','zako','iser','izqw','albr','issd','izad','izbl','isku','isna','hamd','tehn','abrk','shrz','ahvz',
        # 'isbs','kuwt']
        pickle.dump(stations, open(stations_file_path, 'wb'))

    # DATES
    if os.path.isfile(dates_set_file_path):
        dates_sets = pickle.load(open(dates_set_file_path, 'rb'))
    else:
        dates_sets = [None, None]
        itr_date_time = datetime.datetime(2023, 1, 1)
        final_date_time = datetime.datetime(2023, 1, 2)
        date_time_list = []
        while itr_date_time < final_date_time:
            date_time_list.append(itr_date_time)
            itr_date_time = itr_date_time + datetime.timedelta(days=1)
        dates_sets[0] = date_time_list

        itr_date_time = datetime.datetime(2024, 1, 1)
        final_date_time = datetime.datetime(2024, 1, 1)
        date_time_list = []
        while itr_date_time < final_date_time:
            date_time_list.append(itr_date_time)
            itr_date_time = itr_date_time + datetime.timedelta(days=1)
        dates_sets[1] = date_time_list

        pickle.dump(dates_sets, open(dates_set_file_path, 'wb'))

    '''IONEX'''
    for agency in agencies:
        download_ION_SP3_CLK(agency, ION_root, dates_sets)
        pass
    '''SP3'''
    for agency in agencies:
        download_ION_SP3_CLK(agency, SP3_root, dates_sets)
        pass
    '''CLK'''
    for agency in agencies:
        download_ION_SP3_CLK(agency,CLK_root,dates_sets)
        pass

    download_RNX(stations, dates_sets)
    pass
