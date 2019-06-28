
# coding: utf-8

__all__ = ['encode','decode','bbox','neighbors']
_base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
#10进制和32进制转换，32进制去掉了ailo
_decode_map = {}
_encode_map = {}
for i in range(len(_base32)):
    _decode_map[_base32[i]] = i
    _encode_map[i]=_base32[i]
def neighbors(geohash):
    neighbors=[]
    lat_range,lon_range=180,360
    x,y=decode(geohash)
    num=len(geohash)*5
    dx=lat_range/(2**(num//2))
    dy=lon_range/(2**(num-num//2))
    for i in range(1,-2,-1):
        for j in range(-1,2):
            neighbors.append(encode(x+i*dx,y+j*dy,num//5))
#     neighbors.remove(geohash)
    return neighbors
def encode(lat,lon,precision=10):
    """

    :param lat:
    :param lon:
    :param precision: Base32规范编码长度 10位约表示宽1.2m 高59.5cm的区域
    :return:
    """
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    geohash=[]
    code=[]
    j=0
    while len(geohash)<precision:
#         print(code,lat_range,lon_range,geohash)
        j+=1
        lat_mid=sum(lat_range)/2
        lon_mid=sum(lon_range)/2
        #经度
        if lon<=lon_mid:
            code.append(0)
            lon_range[1]=lon_mid
        else:
            code.append(1)
            lon_range[0]=lon_mid
        #纬度
        if lat<=lat_mid:
            code.append(0)
            lat_range[1]=lat_mid
        else:
            code.append(1)
            lat_range[0]=lat_mid
        ##encode
        if len(code)>=5:
            geohash.append(_encode_map[int(''.join(map(str,code[:5])),2)])
            code=code[5:]
    return ''.join(geohash)
def decode(geohash):
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    is_lon=True
    for letter in geohash:
        code=str(bin(_decode_map[letter]))[2:].rjust(5,'0')
        for bi in code:
            if is_lon and bi=='0':
                lon_range[1]=sum(lon_range)/2
            elif is_lon and bi=='1':
                lon_range[0]=sum(lon_range)/2
            elif (not is_lon) and bi=='0':
                lat_range[1]=sum(lat_range)/2
            elif (not is_lon) and bi=='1':
                lat_range[0]=sum(lat_range)/2
            is_lon=not is_lon
    return sum(lat_range)/2,sum(lon_range)/2
def bbox(geohash):
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    is_lon=True
    for letter in geohash:
        code=str(bin(_decode_map[letter]))[2:].rjust(5,'0')
        for bi in code:
            if is_lon and bi=='0':
                lon_range[1]=sum(lon_range)/2
            elif is_lon and bi=='1':
                lon_range[0]=sum(lon_range)/2
            elif (not is_lon) and bi=='0':
                lat_range[1]=sum(lat_range)/2
            elif (not is_lon) and bi=='1':
                lat_range[0]=sum(lat_range)/2
            is_lon=not is_lon
    #左上、右下；(lat_max,lon_min),(lat_min,lon_max)
    return [(lat_range[1],lon_range[0]),(lat_range[0],lon_range[1])]
def GetDirectneighbor(startcode,endcode,directflag):
    """
    获取code 指定方向的邻居
    :param startcode: 起始区域
    :param endcode: 终点区域
    :param directflag: 0代表左上方 1代表上方，2代表右上方 3代表左侧 4代表其本身 5代表右侧 6代表左下方 7代表下方 8代表右下方
    :return:
    """
    codelist = [startcode]
    temcode = startcode
    while temcode != endcode:
        temcode = neighbors(temcode)[directflag]
        codelist.append(temcode)
    return codelist
def LineCode(startendcoor):
    """
    获取起始点至终点的路线编号
    :param startendcoor: 起点终点坐标列表,如[lon1,lat1,lon2,lat2]
    :return:
    """
    startpointCode = encode(startendcoor[1],startendcoor[0],8)
    endpointCode = encode(startendcoor[3],startendcoor[2],8)
    if startpointCode==endpointCode:
        return [startpointCode]
    else:
        londifference = abs(startendcoor[0]-startendcoor[2])
        latdifference = abs(startendcoor[1]-startendcoor[3])
        #比较经度差 和维度差  经度差比较大，方向偏移左右  反之方向偏移上下
        if startendcoor[0] > startendcoor[2] and londifference>latdifference:
            # 终点在起始点左侧
            codelist = GetDirectneighbor(startpointCode,endpointCode,3)
        elif startendcoor[0] < startendcoor[2] and londifference>latdifference:
            codelist = GetDirectneighbor(startpointCode, endpointCode, 5)
        elif startendcoor[1] > startendcoor[3] and londifference<latdifference:
            #终点在起始点下方
            codelist = GetDirectneighbor(startpointCode, endpointCode, 7)
        else: #startendcoor[1] < startendcoor[3] and londifference<latdifference:
            #终点在起始点上方
            codelist = GetDirectneighbor(startpointCode, endpointCode, 1)
        return codelist


# print(encode(39.7214571,116.4288612,8)) #wx4ccrhf
# print(encode(39.7215145,116.4213348,8)) #wx4ccpp6
# print(encode(39.7214571,116.4288612,7)) #wx4ccrhf
# print(encode(39.7215145,116.4213348,7)) #wx4ccpp6
# print(encode(39.7214571,116.4248612,8))
#print(neighbors('wx4ccrh'))
#print(LineCode([116.4288612,39.7214571,116.4213348,39.7215145]))
#print(encode(39.7215145,116.4213348,))
#print(encode(39.7214571,116.4248612,7))