def download_extract_zip(zip_file_url):
    r = requests.get(zip_file_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()
    return z.namelist()[0]
def parser(fn):
    from datetime import datetime
    now_s = datetime.now().strftime("%Y")
    f_s, e_s = now_s[:2], now_s[2:]
    file = open(fn, 'r')
    Route = None
    TyphoonUnit = None
    dataSource = []
    def h(x): 
        return x != '' and x != '\n' and x != '#'
    for line in file.readlines():
        data = line.strip().split(' ')
        #Indicator check
        Indicator_header = ( data[0] == '66666' )
        Indicator_point = ( data[1] == '002' )
        if Indicator_header:            
            if Route != None:
                TyphoonUnit['Route'] = Route
                TyphoonUnit['FirstPointDate'] = Route[0]['Time']
                dataSource.append(TyphoonUnit)
                TyphoonUnit = None
                Route = []
            else:
                Route = []
            header = list(filter(h, data))
            dataType = len(header)
            if dataType == 9:
                TyphoonUnit = {
                    'International_number_ID': header[1],
                    'Data_lines': header[2],
                    'Tropical_cyclone_number_ID':header[3],
                    'International_number_ID_Replicate':header[4],
                    'Flag':header[5],
                    'DurationOfTimeUnit':header[6],
                    'Name':header[7],
                    'LastRevisionDate':header[8],
                    'Type':'9'
                }
            elif dataType == 8:
                TyphoonUnit = {
                    'International_number_ID': header[1],
                    'Data_lines': header[2],
                    'International_number_ID_Replicate':header[3],
                    'Flag':header[4],
                    'DurationOfTimeUnit':header[5],
                    'Name':header[6],
                    'Date':header[7],
                    'Type':'8'
                }
            elif dataType == 7:
                TyphoonUnit = {
                    'International_number_ID': header[1],
                    'Data_lines': header[2],
                    'International_number_ID_Replicate':header[3],
                    'Flag':header[4],
                    'DurationOfTimeUnit':header[5],
                    'Date':header[6],
                    'Type':'7'
                }
        elif Indicator_point:
            pointInfo = list(filter(h, data))
            dataType = len(pointInfo)
            if dataType == 11:
                point = {
                    'Time':pointInfo[0],
                    'Grade':pointInfo[2],
                    'Latitude':pointInfo[3],
                    'Longitude':pointInfo[4],
                    'CentralPressure':pointInfo[5],
                    'Maximum_sustained_wind_speed':pointInfo[6],
                    'Direction_LR50plus':pointInfo[7][0],
                    'Longest_radius_of_50kt':int(pointInfo[7][1:]),
                    'Shortest_radius_of_50kt':int(pointInfo[8]),
                    'Longest_radius_of_30kt':int(pointInfo[9]),
                    'Shortest_radius_of_30kt':int(pointInfo[10]),
                }
            elif dataType == 7:
                point = {
                    'Time':pointInfo[0],
                    'Grade':pointInfo[2],
                    'Latitude':pointInfo[3],
                    'Longitude':pointInfo[4],
                    'CentralPressure':pointInfo[5],
                    'Maximum_sustained_wind_speed':pointInfo[6],
                }
            elif dataType == 6:
                point = {
                    'Time':pointInfo[0],
                    'Grade':pointInfo[2],
                    'Latitude':pointInfo[3],
                    'Longitude':pointInfo[4],
                    'CentralPressure':pointInfo[5],
                }

            time_s_c = point['Time']
            if time_s_c[:2] > e_s:
                time_s_c = str(int(f_s) - 1) + time_s_c
            else:
                time_s_c = f_s + time_s_c
            time_s_c = '{}-{}-{}T{}:00:00'.format(time_s_c[:4],time_s_c[4:6],time_s_c[6:8],time_s_c[8:10])
            point['Time'] = time_s_c

            point['Latitude'] = int(point['Latitude']) / 10
            point['Longitude'] = int(point['Longitude']) / 10
            Route.append(point)
    return dataSource
def convert(dataSource):
    import os, shutil, json
    dir = './dataSource/'
    shutil.rmtree(dir, ignore_errors=True)
    os.makedirs(dir)
    fnList = []
    for tpy in dataSource:
        fn = "".join([ tpy['FirstPointDate'][:4]+'_'+tpy['International_number_ID'] ,".json"])
        fp = open(dir+fn,'w')
        fp.write(json.dumps(tpy, indent=4))
        fp.flush()
        fp.close()
        fnList.append(fn)
    fp = open('file_list.json','w')
    fp.write(json.dumps(fnList, indent=4))
    fp.flush()
    fp.close()
if __name__ == '__main__':
    import requests
    import io
    import zipfile
    url_zip = "http://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks/bst_all.zip"
    print("Downloading...")
    file_name = download_extract_zip(url_zip)#"bst_all.txt"#
    print("Parsing...")
    dataSource = parser(file_name)
    print("Exporting...")
    convert(dataSource)