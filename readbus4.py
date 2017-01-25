readybus.py

import datetime
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','myproject1.settings')
reload(sys)
sys.setdefaultencoding('utf-8')
from bus1.models import Businfo

class Station:
    def __init__(self, routeid, stationid):
        self.route_id = routeid
        self.station_id= stationid
        self.soonbus_pno1 = 'empty'
        self.bus_list =[]
        self.sta_order = ' '
    def append_buslist(self, newdic):
        self.bus_list.append(newdic)

def readfile(bus_id, station_list, sta_list):  # bus_id = m4101 (text)
    import codecs
    idx = 0

    while (idx < len(station_list)):
        station_filename = "/home/ec2-user/cov/bus4/%s/wholedata_a/%s_%s_%s_a_whole.txt" % (
        bus_id, bus_id, sta_list[idx], station_list[idx].station_id)

        f = codecs.open(station_filename,"r","utf-8")

        for line in f.readlines():
            if line == '\n':
                continue

            line = line.strip()
            #parts = line.split(' ')
            parts = line.split('\t')

            if parts[9] != 'None' and parts[14] != 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            pno2 = parts[9],seat2 = parts[10], locno2 = parts[11], pred2 = parts[12], pred_diff = parts[15],
                            waitsec = parts[14])

            elif parts[9] != 'None' and parts[14] == 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            pno2 = parts[9],seat2= parts[10], locno2 = parts[11], pred2= parts[12], pred_diff= parts[15])

            elif parts[9] == 'None' and parts[14] != 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            waitsec= parts[14])
            elif parts[9] == 'None' and parts[14] == 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id)

            a.save()
        idx = idx+1
        f.close()


def main():
    m4101_routeid = 234000875  # M4101
    m4101_stationid = [228000950, 228000911, 228000883, 206000230, 101000002, 100000001, 101000141, 101000264, 101000026, 101000114, 101000148, 101000001, 206000220, 228000905, 228000920, 228002278]
    m4101_sta = [2,3,4,5,11,12,13,14,15,16,17,18,24,25,26,27]

    m5107_routeid = 234001243  # m5107
    m5107_stationid = [203000157, 203000123, 203000122, 203000120, 228000700,
                       101000002, 101000058, 101000128, 101000008, 101000006, 101000148, 101000001, 228000679]
    m5107_sta = [3,4,5,6,7,19,20,21,22,23,26,27,38]

    m4108_routeid = 234001245  # m4108
    m4108_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 101000002, 101000058,
                       101000128, 101000008, 101000006, 101000148, 101000001, 233001282]
    m4108_sta = [3,4,5,6,7,20,21,22,23,24,27,28,41]

    m4403_routeid = 234000995  # m4403
    m4403_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 121000086, 121000941, 121000009,
                       121000005, 121000003, 121000220, 233001282]
    m4403_sta = [3,4,5,6,7,19,20,21,23,24,25,35]

    m4101_station_list = []
    for i in m4101_stationid:
        m4101_station_list.append(Station(m4101_routeid, i))

    m4108_station_list = []
    for i in m4108_stationid:
        m4108_station_list.append(Station(m4108_routeid, i))

    m5107_station_list = []
    for i in m5107_stationid:
        m5107_station_list.append(Station(m5107_routeid, i))

    m4403_station_list = []
    for i in m4403_stationid:
        m4403_station_list.append(Station(m4403_routeid, i))
    readfile("m4101", m4101_station_list, m4101_sta)
    readfile("m4108", m4108_station_list, m4108_sta)
    readfile("m4403", m4403_station_list, m4403_sta)
    readfile("m5107", m5107_station_list, m5107_sta)
#############
#############
if __name__ == "__main__":
    main()

