# scrapy-UserAgent-IpPool-Cookies

随机更换UserAgent
ip代理池
cookies和云打码

transcookies是把cookies字符串转化为scrapy能用的dict

### 解决UnicodeDecodeError: ‘ascii’ codec can’t decode byte 0xe5 in position 108: ordinal not in range(128
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
