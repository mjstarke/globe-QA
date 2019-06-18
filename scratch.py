from globeqa import *
from netCDF4 import Dataset

fpLC = "/Users/mjstarke/Documents/GLOBE_A/land_covers_20181001_20190531.json"
fpMM = "/Users/mjstarke/Documents/GLOBE_A/mosquito_habitat_mapper_20170501_20190531.json"
fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"
fpTH = "/Users/mjstarke/Documents/GLOBE_A/tree_heights_20190323_20190531.json"

fpSC_2018 = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv"
fpGEOS_Jan = "/Users/mjstarke/Documents/GLOBE_B/G5GMAO.cldtt.201801.nc4"

def do_ggc():
    cdf = Dataset(fpGEOS_Jan)
    obs = tools.parse_csv(fpSC_2018)

    plotters.plot_ggc(0, obs, cdf, "/Users/mjstarke/Documents/GLOBE_B/images/GG0000.png")

def do_sc_flags():
    obs = tools.parse_json(fpSC)
    land = tools.prepare_earth_geometry("50m")
    tools.do_quality_check(obs, land)
    tools.print_flag_summary(obs)