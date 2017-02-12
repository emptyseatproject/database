###python 2
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
    # bus4, bus5, test6
    #station_filename = "C:/Users/insha/Dropbox/bus/xml1/%s_2_%s_a_whole.txt" % (bus_id, station_list[0].station_id)
    '''
    for idx in range(station_list):
        station_filename = "/home/ec2-user/cov/bus5/%s/wholedata_a/%s_%s_%s_a_whole.txt" % (
        bus_id, bus_id, station_list[idx].sta_order, station_list[idx].station_id)
    '''

    '''
    detail_a_station_filename = "/home/ec2-user/cov/testdb/%s/onefile_a/%s_a_whole.txt" % (bus_id, bus_id)
    '''#2017-01-23
    while (idx < len(station_list)):
        station_filename = "/home/ec2-user/cov/bus8/%s/wholedata_a/%s_%s_a_whole.txt" % (
        bus_id, bus_id, sta_list[idx])

        '''
        station_filename = "/home/ec2-user/cov/test6/%s/wholedata_a/%s_%s_a_whole.txt" % (
            bus_id, bus_id, sta_list[idx]) // 2017-01-23~
        '''

        f = codecs.open(station_filename,"r","utf-8")

        for line in f.readlines():
            if line == '\n':
                continue

            line = line.strip()
            #parts = line.split(' ')
            parts = line.split('\t')


            if parts[8] == 'None':
                parts[8] = 1
            if parts[12] =='None':
                parts[12] = 1000
            if parts[15] == 'None':
                parts[15] = 999

            if parts[9] != 'None' and parts[14] != 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            pno2 = parts[9],seat2 = parts[10], locno2 = parts[11], pred2 = parts[12], pred_diff = parts[15],
                            waitsec = parts[14],
                            sta_idx = idx)

            elif parts[9] != 'None' and parts[14] == 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            pno2 = parts[9],seat2= parts[10], locno2 = parts[11], pred2= parts[12], pred_diff= parts[15],
                            sta_idx = idx)

            elif parts[9] == 'None' and parts[14] != 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            waitsec= parts[14],
                            sta_idx = idx)
            elif parts[9] == 'None' and parts[14] == 'None':
                a = Businfo(arrival_time=parts[0], weekday=parts[1], routeid=parts[2], stationid=parts[3],
                            flag=parts[4],
                            pno1=parts[5], seat1=parts[6], locno1=parts[7], pred1=parts[8],
                            timestamp=parts[13], arrive_flag=parts[16], sta_order=parts[18], route=bus_id,
                            sta_idx = idx)

            a.save()
        idx = idx+1
        f.close()


def main():
    m4101_routeid = 234000875  # M4101
    m4101_stationid = [228000950, 228000911, 228000883, 206000230, 101000002, 100000001, 101000141, 101000264, 101000026, 101000114, 101000148, 101000001, 206000220, 228000905, 228000920, 228002278]
    m4101_sta = [2,3,4,5,11,12,13,14,15,16,17,18,24,25,26,27]

    m7119_routeid = 218000015  # m7119
    m7119_stationid = [219000711, 219000457, 219000714, 219000356, 219000370, 112000012, 112000016,
                       100000034, 101000128, 101000022, 101000020, 112000017, 112000013, 219000383]
    m7119_sta = [2,3,4,5,6,10,11,12,13,14,17,18,19,23]

    m7106_routeid = 218000012  # m7106
    m7106_stationid = [219000363, 219000192, 219000356, 219000370, 219000368, 112000012, 112000016,
                       100000034, 101000128, 101000022, 101000020, 112000017, 112000013, 219000385]
    m7106_sta = [2,3,4,5,6,7,8,9,10,11,14,15,16,17]

    m7111_routeid = 229000102  # m7111
    m7111_stationid = [229001545, 229001553, 229001422, 229001431, 229001501, 112000012, 112000016, 100000034,
                       101000128, 101000022, 112000017, 112000013, 229001502]
    m7111_sta = [3,4,5,6,7,14,15,16,17,18,23,24,31]

    m6117_routeid = 232000071  # m6117
    m6117_stationid = [232000741, 232000545, 232000553, 232000758, 232000727, 113000424, 113000422,
                       113000420, 113000419, 112000365, 101000250, 112000170, 113000417, 113000416, 113000414,
                       113000412, 232000726]
    m6117_sta =[3,4,6,7,8,17,18,19,20,21,22,24,25,26,27,28,35]


    m5121_routeid = 234001317  # m5121
    m5121_stationid = [203000116, 203000069, 203000294, 203000399, 203000042, 101000002, 101000058,
                       101000128, 101000008, 101000006, 101000148, 101000001, 203000041]
    m5121_sta = [3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 26, 27, 38]

    m5107_routeid = 234001243  # m5107
    m5107_stationid = [203000157, 203000123, 203000122, 203000120, 228000700,
                       101000002, 101000058, 101000128, 101000008, 101000006, 101000148, 101000001, 228000679]
    m5107_sta = [3,4,5,6,7,19,20,21,22,23,26,27,38]

    m4108_routeid = 234001245  # m4108
    m4108_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 101000002, 101000058,
                       101000128, 101000008, 101000006, 101000148, 101000001, 233001282]
    m4108_sta = [3,4,5,6,7,20,21,22,23,24,27,28,41]

    m4102_routeid = 234001159  # m4012
    m4102_stationid = [206000725, 206000299, 206000613, 101000002, 100000001, 101000141, 101000264,
                       101000026, 101000114, 101000148, 101000001, 206000239]
    m4102_sta = [3,4,5,12,13,14,15,16,17,18,19,26]

    m4403_routeid = 234000995  # m4403
    m4403_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 121000086, 121000941, 121000009,
                       121000005, 121000003, 121000220, 233001282]
    m4403_sta = [3,4,5,6,7,19,20,21,23,24,25,35]

    m7625_routeid = 229000112  # m4403
    m7625_stationid = [229001583, 229001497, 229001552, 229001549, 118000089, 118000048, 118000072, 118000065,
                       118000068, 118000071, 118000047, 118000090, 229001550]
    m7625_sta = [3,4,5,6,17,18,19,20,21,22,24,25,37]

    m7426_routeid = 229000111
    m7426_stationid = [229001583, 229000968, 229001506, 229001504, 121000015, 121000013, 121000011, 121000009,
                       121000005, 121000194, 122000612, 122000614, 121000012, 121000014, 121000016, 229001503]
    m7426_sta =[3,4,5,6,25,26,27,28,29,30,31,32,33,34,35,55]

    m5422_routeid = 234001318
    m5422_stationid = [203000116, 203000069, 203000294, 203000399, 203000042, 121000086, 121000945, 121000921,
                       121000510, 121000971, 121000220, 203000041]
    m5422_sta = [3,4,5,6,7,16,17,18,20,21,22,27]

    m6427_routeid = 232000075
    m6427_stationid = [232000741, 232000545, 232000553, 232000758, 232000727, 121000020, 121000018, 121000013,
                       121000011, 121000009, 122000614, 122000654, 121000014, 121000017, 121000019, 119000034,
                       232000726]
    m6427_sta =[3,4,5,6,7,23,24,25,26,27,29,30,31,32,33,34,47]


    m7412_routeid = 234001241
    m7412_stationid = [219000176, 219000131, 219000356, 219000370, 219000368, 121000015, 121000013, 121000011,
                       121000009, 122000187, 122000190, 122000614, 122000616, 121000014, 121000016, 219000385]
    m7412_sta = [3,4,5,6,7,20,21,22,23,26,27,28,29,30,31,48]

    m4101_station_list = []
    for i in m4101_stationid:
        m4101_station_list.append(Station(m4101_routeid, i))

    m7119_station_list = []
    for i in m7119_stationid:
        m7119_station_list.append(Station(m7119_routeid, i))

    m7106_station_list = []
    for i in m7106_stationid:
        m7106_station_list.append(Station(m7106_routeid, i))

    m7111_station_list = []
    for i in m7111_stationid:
        m7111_station_list.append(Station(m7111_routeid, i))

    m6117_station_list = []
    for i in m6117_stationid:
        m6117_station_list.append(Station(m6117_routeid, i))

    m5121_station_list = []
    for i in m5121_stationid:
        m5121_station_list.append(Station(m5121_routeid, i))

    m4108_station_list = []
    for i in m4108_stationid:
        m4108_station_list.append(Station(m4108_routeid, i))

    m4102_station_list = []
    for i in m4102_stationid:
        m4102_station_list.append(Station(m4102_routeid, i))

    m5107_station_list = []
    for i in m5107_stationid:
        m5107_station_list.append(Station(m5107_routeid, i))

    m4403_station_list = []
    for i in m4403_stationid:
        m4403_station_list.append(Station(m4403_routeid, i))

    m7625_station_list = []
    for i in m7625_stationid:
        m7625_station_list.append(Station(m7625_routeid, i))

    m7426_station_list = []
    for i in m7426_stationid:
        m7426_station_list.append(Station(m7426_routeid, i))

    m5422_station_list = []
    for i in m5422_stationid:
        m5422_station_list.append(Station(m5422_routeid, i))

    m6427_station_list = []
    for i in m6427_stationid:
        m6427_station_list.append(Station(m6427_routeid, i))

    m7412_station_list = []
    for i in m7412_stationid:
        m7412_station_list.append(Station(m7412_routeid, i))

    readfile("m4101", m4101_station_list, m4101_sta)
    readfile("m4108", m4108_station_list, m4108_sta)
    readfile("m4403", m4403_station_list, m4403_sta)
    readfile("m5107", m5107_station_list, m5107_sta)

    readfile("m4102", m4102_station_list, m4102_sta)
    readfile("m5121", m5121_station_list, m5121_sta)
    readfile("m5422", m5422_station_list, m5422_sta)
    readfile("m7106", m7106_station_list, m7106_sta)

    readfile("m7111", m7111_station_list, m7111_sta)
    readfile("m7119", m7119_station_list, m7119_sta)
    readfile("m7412", m7412_station_list, m7412_sta)
    readfile("m7426", m7426_station_list, m7426_sta)

    readfile("m7625", m7625_station_list, m7625_sta)
    readfile("m6427", m6427_station_list, m6427_sta)
    readfile("m6117", m6117_station_list, m6117_sta)


#############
#############
if __name__ == "__main__":
    main()

