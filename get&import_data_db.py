import keyfile
import time
import urllib.request  # python 3
import xml.etree.ElementTree as etree
import datetime

import psycopg2 as pg2



cnt = 0
class Station:
    def __init__(self, routeid, stationid, route):
        self.route_id = routeid
        self.station_id = stationid
        self.soonbus_pno1 = 'empty'
        self.bus_list = []
        self.sta_order = ' '
        self.busname = route

    def get_arrivalurl(self):
        ### NEED API KEYS ###
        global cnt
        if cnt<70000:
            key = keyfile.info_1st_api
        elif cnt>=70000 and cnt < 140000:
            key = keyfile.info_2nd_api
        elif cnt>=140000 and cnt < 210000:
            key = keyfile.info_3rd_api
        elif cnt>=210000 and cnt < 280000:
            key = keyfile.info_4th_api
        elif cnt>=280000 and cnt < 350000:
            key = keyfile.info_5th_api
        elif cnt>=350000 and cnt < 420000:
            key = keyfile.info_6th_api
        elif cnt>=420000 and cnt < 490000:
            key = keyfile.info_7th_api
        elif cnt>=490000:
            key = keyfile.info_8th_api


        url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey=%s&routeId=%s&stationId=%s" % (
        key, self.route_id, self.station_id)
        data = urllib.request.urlopen(url).read()  # python3
        # data = urllib2.urlopen(url).read() # python2
        time.sleep(0.01)

        filename = "%s_busarrival.xml" % self.route_id
        f = open(filename, 'wb')
        f.write(data)
        f.close()

        tree = etree.parse(filename)
        cnt += 1
        print(key, cnt)
        return tree

    def extract_bus_info(self, tree, conn):

        busarrivalitem = tree.find('msgBody/busArrivalItem')


        qtime = tree.findtext('msgHeader/queryTime')


        flag = busarrivalitem.find('flag').text
        locno1 = busarrivalitem.find('locationNo1').text
        locno2 = busarrivalitem.find('locationNo2').text
        pno1 = busarrivalitem.find('plateNo1').text
        pno2 = busarrivalitem.find('plateNo2').text
        pred1 = busarrivalitem.find('predictTime1').text
        pred2 = busarrivalitem.find('predictTime2').text
        seat1 = busarrivalitem.find('remainSeatCnt1').text
        seat2 = busarrivalitem.find('remainSeatCnt2').text
        routeid = busarrivalitem.find('routeId').text
        stationid = busarrivalitem.find('stationId').text
        station_order = busarrivalitem.find('staOrder').text

        self.sta_order = station_order
        dt = datetime.datetime.now()
        kor = dt + datetime.timedelta(hours=9)

        arrival_time = datetime.datetime.strptime(qtime, '%Y-%m-%d %H:%M:%S.%f')
        round_time = self.roundTime(arrival_time, 10 * 60)

        pred_diff = None
        if pred1 != None and pred2 != None:
            pred_diff = int(pred2) - int(pred1)



        if kor.weekday() == 5:
            add_pred1 = arrival_time + datetime.timedelta(minutes = int(pred1))
            round_pred1 = self.roundTime(add_pred1, 15*60)

            if pred2 !=None:
                add_pred2 = arrival_time + datetime.timedelta(minutes = int(pred2))
                round_pred2 = self.roundTime(add_pred2, 15*60)
            else:
                round_pred2 = None
        elif kor.weekday() == 6:
            add_pred1 = arrival_time + datetime.timedelta(minutes=int(pred1))
            round_pred1 = self.roundTime(add_pred1, 30 * 60)

            if pred2 != None:
                add_pred2 = arrival_time + datetime.timedelta(minutes=int(pred2))
                round_pred2 = self.roundTime(add_pred2, 30 * 60)
            else:
                round_pred2 = None
        else:
            add_pred1 = arrival_time + datetime.timedelta(minutes=int(pred1))
            round_pred1 = self.roundTime(add_pred1, 10 * 60)

            if pred2 != None:
                add_pred2 = arrival_time + datetime.timedelta(minutes=int(pred2))
                round_pred2 = self.roundTime(add_pred2, 10 * 60)
            else:
                round_pred2 = None

        ###      0          1           2         3       4      5     6       7       8    9       10      11      12      13                      14  15         16       17       18                19
        bus = [qtime, kor.weekday(), routeid, stationid, flag, pno1, seat1, locno1, pred1, pno2, seat2, locno2, pred2, int(arrival_time.timestamp()), None, pred_diff, 0, station_order, self.busname, round_time, round_pred1, round_pred2]

        return bus

    def insert_realtime_station (self, bus, conn):
        cur = conn.cursor()
        sql = """
                    INSERT INTO realtime_station (arrival_time, weekday, routeid, stationid, flag, pno1, seat1, locno1, pred1, pno2,seat2,locno2,pred2,pred_diff,sta_order,route, ten_minutes, round_pred1, round_pred2)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                    """
        data = (bus[0],bus[1],bus[2],bus[3],bus[4],bus[5],bus[6],bus[7],bus[8],bus[9],bus[10],bus[11],bus[12],bus[15],bus[17], bus[18], bus[19], bus[20], bus[21])
        cur.execute(sql, data)
        conn.commit()


    def append_buslist(self, newdic):
        self.bus_list.append(newdic)

    def is_newbus(self, tree):  # busarrivialitem is new information, soonbus is new information
        busarrivalitem = tree.find('msgBody/busArrivalItem')

        error_code = tree.findtext('msgHeader/resultCode')
        if error_code != '0':
            if error_code != '4':
                print(tree.findtext('comMsgHeader/errMsg'))
                return False

        if self.soonbus_pno1 == 'empty':
            if tree.findtext('msgHeader/resultCode') == '4':
                return False
            elif busarrivalitem == None:
                return False
            elif busarrivalitem.findtext('locationNo1') == '1':
                return True
            else:
                return False

        if tree.findtext('msgHeader/resultCode') == '4':
            return True
        elif self.soonbus_pno1 != busarrivalitem.findtext('plateNo1'):
            return True
        else:
            return False
        return False

    def get_buslisturl(self):
        key = keyfile.loc_1st_api
        url = "http://openapi.gbis.go.kr/ws/rest/buslocationservice?serviceKey=%s&routeId=%s" % (key, self.route_id)
        data = urllib.request.urlopen(url).read()  # python3
        # data = urllib2.urlopen(url).read() # python2
        time.sleep(0.05)

        filename = "%s_locations.xml" % self.route_id
        f = open(filename, 'wb')
        f.write(data)
        f.close()

        tree = etree.parse(filename)
        return tree

    def insert_realtime_buslist(self, conn):
        tree = self.get_buslisturl()
        idx = 0
        while idx <= 5:
            if tree.findtext('comMsgHeader/returnCode') != '00':
                print("No list ", idx, self.busname)
                tree = self.get_buslisturl()
                idx = idx + 1
            elif tree.findtext('comMsgHeader/returnCode') == '00':
                break
            else:
                return

        lst = tree.findall('msgBody/busLocationList')
        cur = conn.cursor()
        sql = """
                 INSERT INTO realtime_buslist (arrival_time,routeid,stationid,pno1,seat1,sta_order,route)
                 values (%s,%s,%s,%s,%s,%s,%s);
                 """

        for busarrivalitem in lst:
            data = (tree.findtext('msgHeader/queryTime'), busarrivalitem.find('routeId').text, busarrivalitem.find('stationId').text,
                    busarrivalitem.find('plateNo').text, busarrivalitem.find('remainSeatCnt').text,
                    busarrivalitem.find('stationSeq').text, self.busname)
            cur.execute(sql, data)
            conn.commit()

    def insert_arrivedbus(self, conn, bus):

        cur = conn.cursor()
        sql = """
                            INSERT INTO test_bus (arrival_time,weekday,routeid,stationid,flag,pno1,seat1,locno1,pred1, pno2,seat2,locno2,pred2, waitsec, pred_diff, arrive_flag, sta_order,route, ten_minutes)
                            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                            """
        data = (bus[0], bus[1], bus[2], bus[3], bus[4], bus[5], bus[6], bus[7], bus[8], bus[9], bus[10], bus[11], bus[12], bus[14], bus[15], bus[16], bus[17], bus[18], bus[19])
        cur.execute(sql, data)
        conn.commit()


    def roundTime(self, dt=None, roundTo=60): #dt = datetime.dattime object, roundTo ex) 10*60  round 10 minutes.
        if dt == None: dt = datetime.datetime.now()
        seconds = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        round_datetime = dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond) #날짜까지...
        only_time = round_datetime.time()
        return only_time



    def operate(self, conn):
        try:
            tree = self.get_arrivalurl()
        except:
            # print("operate except")
            time.sleep(0.02)
            try:
                tree = self.get_arrivalurl()
            except:
                return False

        if tree.findtext('msgHeader/resultCode') == '8':
            tree = self.get_arrivalurl()
        if tree.findtext('msgHeader/resultCode') == '8':
            tree = self.get_arrivalurl()

        idx = 0

        while idx <=5:
            if tree.findtext('msgBody/busArrivalItem/flag') == None and tree.findtext('msgHeader/resultCode') != '4':
                print("No flag ", idx)
                tree = self.get_arrivalurl()
                idx = idx + 1
            else:
                break
        '''
        if tree.findtext('msgBody/busArrivalItem/flag') == None and tree.findtext('msgHeader/resultCode') != '4':
            print("No flag 1")
            tree = self.get_arrivalurl()
            if tree.findtext('msgBody/busArrivalItem/flag') == None and tree.findtext('msgHeader/resultCode') != '4':
                print("No flag 2")
                tree = self.get_arrivalurl()
                if tree.findtext('msgBody/busArrivalItem/flag') == None and tree.findtext('msgHeader/resultCode') != '4':
                    print("No flag 3")
                    tree = self.get_arrivalurl()
                    if tree.findtext('msgBody/busArrivalItem/flag')== None and tree.findtext('msgHeader/resultCode') != '4':
                        print("No flag 4")
                        tree = self.get_arrivalurl()
                        if tree.findtext('msgBody/busArrivalItem/flag') == None and tree.findtext('msgHeader/resultCode') != '4':
                            return False
        '''

        if tree.findtext('msgHeader/resultCode') != '4' and tree.findtext('msgBody/busArrivalItem/flag') != None:
            #print(self.busname, self.station_id, self.sta_order)

            busdata = self.extract_bus_info(tree,conn)
            self.insert_realtime_station(busdata,conn)



        try:
            if len(self.bus_list) >= 1:
                if self.bus_list[-1][5] == tree.findtext('msgBody/busArrivalItem/plateNo1'):
                    #busdata = self.extract_bus_info(tree, conn)
                    self.bus_list[-1] = busdata
        except:
            print("it's okay")


        if self.is_newbus(tree):  # arriving new bus
            if len(self.bus_list) >= 2:
                if self.bus_list[-1][16] == 0 or self.bus_list[-1][16] == 2:
                    self.bus_list[-1][0] = tree.findtext('msgHeader/queryTime')
                    self.bus_list[-1][13] = int(time.time())
                    self.bus_list[-1][14] = self.bus_list[-1][13] - self.bus_list[-2][13]
                    self.bus_list[-1][16] = 1
                    if self.bus_list[-1][7] == '1':
                        self.insert_arrivedbus(conn, self.bus_list[-1])
                self.bus_list[-1][14] = self.bus_list[-1][13] - self.bus_list[-2][13]

            elif len(self.bus_list) == 1:
                if self.bus_list[0][16] == 0 or self.bus_list[0][16] == 2:
                    self.bus_list[0][0] = tree.findtext('msgHeader/queryTime')
                    self.bus_list[0][13] = int(time.time())
                    self.bus_list[0][16] = 1
                    if self.bus_list[-1][7] == '1':
                        self.insert_arrivedbus(conn, self.bus_list[-1])


            if tree.findtext('msgHeader/resultCode') == '4':  # no arriving bus
                self.soonbus_pno1 = 'empty'

            else:
                newbus = self.extract_bus_info(tree, conn)
                self.append_buslist(newbus)
                self.soonbus_pno1 = newbus[5]

        else:
            return False


def make_file(bus_id, station_list):
    dt = datetime.datetime.now()
    kor = dt + datetime.timedelta(hours=9)

    if kor.hour >= 0 and kor.hour <= 3:
        kor = dt

    idx = 0
    detail_a_station_filename = "/home/ec2-user/cov/bus10/%s/eachday_wholedata_w/%s_%s_w.txt" % (
        bus_id, bus_id, kor.date())
    d_station = open(detail_a_station_filename, 'w')

    while (idx < len(station_list)):

        for k in range(len(station_list[idx].bus_list)):
            for i in range(len(station_list[idx].bus_list[k])):
                d_station.write(str(station_list[idx].bus_list[k][i]))
                d_station.write("\t")
            d_station.write("\n")
        d_station.write("\n\n")
        idx += 1

    d_station.close()


def make_each_station_file_a(bus_id, station_list):
    idx = 0
    while (idx < len(station_list)):
        # /home/ec2-user/cov/bus10/%s/
        detail_a_station_filename = "/home/ec2-user/cov/bus10/%s/wholedata_a/%s_%s_a_whole.txt" % (
            bus_id, bus_id, station_list[idx].sta_order)
        d_station = open(detail_a_station_filename, 'a')

        for k in range(len(station_list[idx].bus_list)):
            for i in range(len(station_list[idx].bus_list[k])):
                d_station.write(str(station_list[idx].bus_list[k][i]))
                d_station.write("\t")
            d_station.write("\n")
        d_station.write("\n\n")
        d_station.close()

        idx += 1

    idx = 0
    detail_a_station_filename = "/home/ec2-user/cov/bus10/%s/onefile_a/%s_a_whole.txt" % (
        bus_id, bus_id)
    d_station = open(detail_a_station_filename, 'a')

    while (idx < len(station_list)):

        for k in range(len(station_list[idx].bus_list)):
            for i in range(len(station_list[idx].bus_list[k])):
                d_station.write(str(station_list[idx].bus_list[k][i]))
                d_station.write("\t")
            d_station.write("\n")
        d_station.write("\n\n")

        idx += 1
    d_station.close()







def main():
    global cnt
    ########################
    #########################

    
    m4101_routeid = 234000875  # M4101
    m4101_stationid = [228000950, 228000911, 228000883, 206000230, 101000002, 100000001, 101000141, 101000264,
                       101000026, 101000114, 101000148, 101000001, 206000220, 228000905, 228000920, 228002278]
    m4101_sta = [2, 3, 4, 5, 11, 12, 13, 14, 15, 16, 17, 18, 24, 25, 26, 27]

    m7119_routeid = 218000015  # m7119
    m7119_stationid = [219000711, 219000457, 219000714, 219000356, 219000370, 112000012, 112000016,
                       100000034, 101000128, 101000022, 101000020, 112000017, 112000013, 219000383]
    m7119_sta = [2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 17, 18, 19, 23]

    m7106_routeid = 218000012  # m7106
    m7106_stationid = [219000363, 219000192, 219000356, 219000370, 219000368, 112000012, 112000016,
                       100000034, 101000128, 101000022, 101000020, 112000017, 112000013, 219000385]
    m7106_sta = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17]

    m7111_routeid = 229000102  # m7111
    m7111_stationid = [229001545, 229001553, 229001422, 229001431, 229001501, 112000012, 112000016, 100000034,
                       101000128, 101000022, 112000017, 112000013, 229001502]
    m7111_sta = [3, 4, 5, 6, 7, 14, 15, 16, 17, 18, 23, 24, 31]

    m6117_routeid = 232000071  # m6117
    m6117_stationid = [232000741, 232000545, 232000553, 232000758, 232000727, 113000424, 113000422,
                       113000420, 113000419, 112000365, 101000250, 112000170, 113000417, 113000416, 113000414,
                       113000412, 232000726]
    m6117_sta = [3, 4, 6, 7, 8, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 35]

    m5121_routeid = 234001317  # m5121
    m5121_stationid = [203000116, 203000069, 203000294, 203000399, 203000042, 101000002, 101000058,
                       101000128, 101000008, 101000006, 101000148, 101000001, 203000041]
    m5121_sta = [3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 26, 27, 38]

    m5107_routeid = 234001243  # m5107
    m5107_stationid = [203000157, 203000123, 203000122, 203000120, 228000700,
                       101000002, 101000058, 101000128, 101000008, 101000006, 101000148, 101000001, 228000679]
    m5107_sta = [3, 4, 5, 6, 7, 19, 20, 21, 22, 23, 26, 27, 38]

    m4108_routeid = 234001245  # m4108
    m4108_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 101000002, 101000058,
                       101000128, 101000008, 101000006, 101000148, 101000001, 233001282]
    m4108_sta = [3, 4, 5, 6, 7, 20, 21, 22, 23, 24, 27, 28, 41]

    m4102_routeid = 234001159  # m4012
    m4102_stationid = [206000725, 206000299, 206000613, 101000002, 100000001, 101000141, 101000264,
                       101000026, 101000114, 101000148, 101000001, 206000239]
    m4102_sta = [3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 26]

    m4403_routeid = 234000995  # m4403
    m4403_stationid = [233001450, 233001224, 233001219, 233001562, 233001281, 121000086, 121000941, 121000009,
                       121000005, 121000003, 121000220, 233001282]
    m4403_sta = [3, 4, 5, 6, 7, 19, 20, 21, 23, 24, 25, 35]

    m7625_routeid = 229000112  # m4403
    m7625_stationid = [229001583, 229001497, 229001552, 229001549, 118000089, 118000048, 118000072, 118000065,
                       118000068, 118000071, 118000047, 118000090, 229001550]
    m7625_sta = [3, 4, 5, 6, 17, 18, 19, 20, 21, 22, 24, 25, 37]

    m7426_routeid = 229000111
    m7426_stationid = [229001583, 229000968, 229001506, 229001504, 121000015, 121000013, 121000011, 121000009,
                       121000005, 121000194, 122000612, 122000614, 121000012, 121000014, 121000016, 229001503]
    m7426_sta = [3, 4, 5, 6, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 55]

##############################
#############################
    m5422_routeid = 234001318
    m5422_stationid = [203000116, 203000069, 203000294, 203000399, 203000042, 121000086, 121000945, 121000921,
                       121000510, 121000971, 121000220, 203000041, 203000400, 203000295, 203000177, 203000083, 203000028]
    m5422_sta = [3, 4, 5, 6, 7, 16, 17, 18, 20, 21, 22, 27, 28, 29, 30, 31, 32]

    m6427_routeid = 232000075
    m6427_stationid = [232000741, 232000545, 232000553, 232000758, 232000727, 121000020, 121000018, 121000013,
                       121000011, 121000009, 122000614, 122000654, 121000014, 121000017, 121000019, 119000034,
                       232000726]
    m6427_sta = [3, 4, 5, 6, 7, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 47]

    m7412_routeid = 234001241
    m7412_stationid = [219000176, 219000131, 219000356, 219000370, 219000368, 121000015, 121000013, 121000011,
                       121000009, 122000187, 122000190, 122000614, 122000616, 121000014, 121000016, 219000385]
    m7412_sta = [3, 4, 5, 6, 7, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 48]

    ####
    ####
    ####
    ####
    while (True):
        # print("append list")

        m4101_station_list = []
        for i in m4101_stationid:
            m4101_station_list.append(Station(m4101_routeid, i, "m4101"))

        m7119_station_list = []
        for i in m7119_stationid:
            m7119_station_list.append(Station(m7119_routeid, i, "m7119"))

        m7106_station_list = []
        for i in m7106_stationid:
            m7106_station_list.append(Station(m7106_routeid, i, "m7106"))

        m7111_station_list = []
        for i in m7111_stationid:
            m7111_station_list.append(Station(m7111_routeid, i, "m7111"))

        m6117_station_list = []
        for i in m6117_stationid:
            m6117_station_list.append(Station(m6117_routeid, i, "m6117"))

        m5121_station_list = []
        for i in m5121_stationid:
            m5121_station_list.append(Station(m5121_routeid, i, "m5121"))

        m4108_station_list = []
        for i in m4108_stationid:
            m4108_station_list.append(Station(m4108_routeid, i, "m4108"))

        m4102_station_list = []
        for i in m4102_stationid:
            m4102_station_list.append(Station(m4102_routeid, i, "m4102"))

        m4403_station_list = []
        for i in m4403_stationid:
            m4403_station_list.append(Station(m4403_routeid, i, "m4403"))

        m7625_station_list = []
        for i in m7625_stationid:
            m7625_station_list.append(Station(m7625_routeid, i, "m7625"))

        m7426_station_list = []
        for i in m7426_stationid:
            m7426_station_list.append(Station(m7426_routeid, i, "m7426"))

        m5422_station_list = []
        for i in m5422_stationid:
            m5422_station_list.append(Station(m5422_routeid, i, "m5422"))

        m6427_station_list = []
        for i in m6427_stationid:
            m6427_station_list.append(Station(m6427_routeid, i, "m6427"))

        m7412_station_list = []
        for i in m7412_stationid:
            m7412_station_list.append(Station(m7412_routeid, i, "m7412"))

        m5107_station_list = []
        for i in m5107_stationid:
            m5107_station_list.append(Station(m5107_routeid, i, "m5107"))


        dt = datetime.datetime.now()
        kor = dt + datetime.timedelta(hours=9)
        ####kor = dt + datetime.timedelta(hours=0)

        conn = pg2.connect(host=keyfile.hostid, port=keyfile.portid, database=keyfile.databaseid, user=keyfile.userid, password=keyfile.passwordid)  # myprojectuser1
        cur = conn.cursor()
        cur.execute("""DELETE FROM realtime_buslist;""")
        cur.execute("""DELETE FROM realtime_station;""")
        conn.commit()
        cur.close()
        conn.close()
        while ((kor.hour >= 4) or (kor.hour < 1)):
            conn = pg2.connect(host=keyfile.hostid, port=keyfile.portid, database=keyfile.databaseid, user=keyfile.userid,
                               password=keyfile.passwordid)  # myprojectuser1
            cur = conn.cursor()


            dt = datetime.datetime.now()
            kor = dt + datetime.timedelta(hours=9)
            ####kor = dt + datetime.timedelta(hours=0)
            ####            if(kor.hour == 21 and kor.minute >= 37):
            ####               break
            if kor.hour == 1:
                break


            for k in range(len(m5422_station_list)):
                m5422_station_list[k].operate(conn)
            m5422_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m4101_station_list)):
                m4101_station_list[k].operate(conn)
            m4101_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m7412_station_list)):
                m7412_station_list[k].operate(conn)
            m7412_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m7119_station_list)):
                m7119_station_list[k].operate(conn)
            m7119_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m7106_station_list)):
                m7106_station_list[k].operate(conn)
            m7106_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m7111_station_list)):
                m7111_station_list[k].operate(conn)
            m7111_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m6117_station_list)):
                m6117_station_list[k].operate(conn)
            m6117_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m5121_station_list)):
                m5121_station_list[k].operate(conn)
            m5121_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m4108_station_list)):
                m4108_station_list[k].operate(conn)
            m4108_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m4102_station_list)):
                m4102_station_list[k].operate(conn)
            m4102_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m4403_station_list)):
                m4403_station_list[k].operate(conn)
            m4403_station_list[0].insert_realtime_buslist(conn)
            
            for k in range(len(m7625_station_list)):
                m7625_station_list[k].operate(conn)
            m7625_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m7426_station_list)):
                m7426_station_list[k].operate(conn)
            m7426_station_list[0].insert_realtime_buslist(conn)

            for k in range(len(m6427_station_list)):
                m6427_station_list[k].operate(conn)
            m6427_station_list[0].insert_realtime_buslist(conn)                

            for k in range(len(m5107_station_list)):
                m5107_station_list[k].operate(conn)
            m5107_station_list[0].insert_realtime_buslist(conn)
            
            make_file("m4101", m4101_station_list)
            make_file("m7119", m7119_station_list)
            make_file("m7106", m7106_station_list)
            make_file("m7111", m7111_station_list)

            make_file("m6117", m6117_station_list)
            make_file("m5121", m5121_station_list)
            make_file("m4108", m4108_station_list)
            make_file("m4102", m4102_station_list)

            make_file("m4403", m4403_station_list)
            make_file("m7625", m7625_station_list)
            make_file("m7426", m7426_station_list)

            make_file("m5422", m5422_station_list)
            make_file("m6427", m6427_station_list)
            make_file("m7412", m7412_station_list)

            make_file("m5107", m5107_station_list)
            
            # Freq = 2500
            # Dur = 1000
            # winsound.Beep(Freq,Dur)
            print(kor)

            cur.execute("""
            UPDATE realtime_buslist
            SET new_flag = CASE new_flag WHEN false then true
                                         WHEN true then false
                            END;
            """)
            conn.commit()
            cur.execute("""
            DELETE FROM realtime_buslist
            WHERE new_flag = false
            """)
            conn.commit()

            cur.execute("""
                        UPDATE realtime_station
                        SET new_flag = CASE new_flag WHEN false then true
                                                     WHEN true then false
                                        END;
                        """)
            conn.commit()
            cur.execute("""
                        DELETE FROM realtime_station
                        WHERE new_flag = false
                        """)
            conn.commit()

            print("*********************************************************************sleep 2***************************************************")
            cur.close()
            conn.close()
            time.sleep(2)

        #############
        #############
        print("sleep3:50")
        cnt = 0
        time.sleep(13700)  # start 04:50


#############
#############
if __name__ == "__main__":
    main()


