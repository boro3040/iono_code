import os
import glob
import json
import subprocess
import platform
import pickle

from utilities.utils import date_to_ionex_name, date_to_rinex_name, date_to_clk, date_to_sp3, date_to_glab_output_file, \
    prioritized_sp3_filenames
from utilities.utils import ION_root, RNX_root, SP3_root, CLK_root, OUTPUT_root

print(os.path.abspath(os.curdir), platform.system())

GLAB_DIR = 'gLAB'
SPP_JSON_FILE = 'SPP_config.json'
SPP_CONF_FILE = 'tmp_config.cfg'
# GLAB_RUN_FILE   = 'gLab_run.sh'
# GLAB_LINUX_FIEL = 'gLAB_linux'
# GLAB_LINUX_FIEL = 'gLAB_run.bat'


SPP_JSON_FILE_PATH = os.path.join(GLAB_DIR, SPP_JSON_FILE)
SPP_CONF_FILE_PATH = os.path.join(GLAB_DIR, SPP_CONF_FILE)
# GLAB_RUN_FILE_PATH =   os.path.join(GLAB_DIR,GLAB_RUN_FILE   )
# GLAB_LINUX_FIEL_PATH = os.path.join(GLAB_DIR, GLAB_LINUX_FIEL)


def write_dict_to_file(file_path, data_dict):
    f = open(file_path, 'w')
    for k, v in data_dict.items():
        str_to_write = '{} {}\r\n'.format(k, v)
        f.write(str_to_write)
    f.close()

'''
def date_to_conf_dict(date, station, agency, json_dict, sp3_clk_agency='igs', no_clk_sp3=False):
    _, obs, _, _ = date_to_rinex_name(date, station)
    orb = date_to_sp3(date, sp3_clk_agency)
    clk = date_to_clk(date, sp3_clk_agency)
    inx, year, _ = date_to_ionex_name(date, agency)

    out = date_to_glab_output_file(date, station, agency)

    obs = os.path.join("..", RNX_root, obs)
    orb = os.path.join("..", SP3_root, orb)
    clk = os.path.join("..", CLK_root, clk)
    inx = os.path.join("..", ION_root, inx)
    out = os.path.join(OUTPUT_root, '{}'.format(station), '{}'.format(year), out)
    original_out = out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    out = os.path.join("..", out)

    keys = list(json_dict.keys())
    inputs = [obs, orb, clk, inx]
    for idx, i in enumerate(inputs):
        key = keys[idx]
        json_dict[key] = i

    json_dict[keys[-1]] = out

    if agency == 'nic': del json_dict['-input:inx']
    if no_clk_sp3:
        del json_dict['-input:orb']
        del json_dict['-input:clk']
    print(json_dict)

    return json_dict, original_out
'''


def date_to_conf_dict_v2(date, station, agency, json_dict, sp3_clk_agency='igs'):
    _, obs, _, _ = date_to_rinex_name(date, station)
    _, orb_list = prioritized_sp3_filenames(date)
    orb = orb_list[0]
    clk = date_to_clk(date, sp3_clk_agency)
    inx, year, _ = date_to_ionex_name(date, agency)

    out = date_to_glab_output_file(date, station, agency)

    obs = os.path.join(".", RNX_root, obs)
    orb = os.path.join(".", SP3_root, orb)
    for sp3 in orb_list:
        sp3_file_path = os.path.join(".", SP3_root, sp3)
        # print(sp3_file_path)
        if os.path.isfile(sp3_file_path):
            orb = sp3_file_path
            break

    clk = os.path.join(".", CLK_root, clk)
    inx = os.path.join(".", ION_root, inx)
    out = os.path.join(".", OUTPUT_root, '{}'.format(station), '{}'.format(year), out)
    original_out = out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    #out = os.path.join(".", out)

    keys = list(json_dict.keys())
    inputs = [obs, orb, clk, inx]
    for idx, i in enumerate(inputs):
        key = keys[idx]
        json_dict[key] = i

    json_dict[keys[-1]] = out

    if agency == 'nic': del json_dict['-input:inx']
    if not os.path.isfile(clk):
        del json_dict['-input:clk']
        del json_dict['-input:orb']

        json_dict['-input:sp3'] = orb

    print(json_dict)
    return json_dict, original_out


dates_set = pickle.load(open('dates_set_single.pk', 'rb'))
stations = pickle.load(open('stations_single.pk', 'rb'))
# dates_set = pickle.load(open('dates_set.pk','rb'))
# stations = pickle.load(open('stations.pk','rb'))
SPP_dict = json.load(open(SPP_JSON_FILE_PATH, 'rb'))
agencies = pickle.load(open('agencies.pk', 'rb')) + ['nic']

date = dates_set[1][0]
station = stations[0]

print(date, station)

json_dict_to_save, original_out = date_to_conf_dict_v2(date, station, 'nic', SPP_dict)
# date_to_conf_dict_v2(date,station,'igs',SPP_dict)

print(write_dict_to_file(SPP_CONF_FILE_PATH, json_dict_to_save), original_out, agencies)

# dates_set = pickle.load(open('dates_set.pk','rb'))
# stations = pickle.load(open('stations.pk','rb'))
# SPP_dict = json.load(open(SPP_JSON_FILE_PATH,'rb'))
# agencies = ['igs','ckm']

for seq in dates_set:
    for date in seq:
        for agency in agencies:
            for station in stations:
                SPP_dict = json.load(open(SPP_JSON_FILE_PATH, 'rb'))
                # json_dict_to_save,original_out = date_to_conf_dict(date,station,agency,SPP_dict)
                # json_dict_to_save,original_out = date_to_conf_dict(date,station,agency,SPP_dict,no_clk_sp3=True)
                json_dict_to_save, original_out = date_to_conf_dict_v2(date, station, agency, SPP_dict)
                if os.path.isfile(original_out): continue
                write_dict_to_file(SPP_CONF_FILE_PATH, json_dict_to_save)
                try:
                    command = r'gLAB.exe -input:cfg .{}gLAB{}{}'.format(os.sep, os.sep, SPP_CONF_FILE)
                    # print(command)
                    # subprocess.call([r'gLAB.exe -input:cfg .\\gLAB\\{}'.format(SPP_CONF_FILE)],shell=True)
                    # subprocess.call([command], shell=True)
                    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    p.communicate()
                except Exception as e:
                    # print(e)
                    pass