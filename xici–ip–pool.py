# -*- coding:utf-8 -*-

import requests
from scrapy.selector import Selector
import pymysql

conn=pymysql.connect(host="localhost",user="root",password="root123",db="scrapy",port=3306,charset="utf8")
cursor=conn.cursor()


def crawl_ips():
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    for i in range(5):
        re=requests.get('http://www.xicidaili.com/nn/{0}'.format(i),headers=headers)

        selector=Selector(text=re.text)
        all_trs=selector.css("#ip_list tr")
        ip_list=[]
        for tr in all_trs[1:]:
            speed_str=tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed=float(speed_str.split("秒")[0])

            all_texts=tr.css("td::text").extract()
            ip=all_texts[0]
            port=all_texts[1]
            proxy_type=all_texts[5]
            ip_list.append((ip,port,proxy_type,speed))

        for ip_info in ip_list:

            insert_sql="""insert into xici_ip_pool(ip,port,speed,proxy_type) values('{0}','{1}',{2},'HTTP')""".format(ip_info[0],ip_info[1],ip_info[3])
            cursor.execute(insert_sql)
            conn.commit()



class GetIp(object):
    def delete_ip(self,ip):
        #从数据库中删除无效的ip
        delete_sql="""
                delete from xici_ip_pool where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self,ip,port):
        #判断ip是否可用
        http_url="http://www.baidu.com"
        proxy_url="http://{0}:{1}".format(ip,port)
        try:
            proxy_dict={
                "http":proxy_url,
            }
            response=requests.get(http_url,proxies=proxy_dict)
        except Exception as e:
            print ("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code=response.status_code
            if code >=200 and code <300:
                print ("effective ip")
                return True
            else:
                print ("invalid ip and port")
                self.delete_ip(ip)
                return False


    def get_random_ip(self):
        #从数据库中随机获取一个可用的ip
        random_sql="""
            SELECT ip,port FROM xici_ip_pool
            ORDER BY RAND()
            LIMIT 1
            """
        result=cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip=ip_info[0]
            port=ip_info[1]

            judge_re=self.judge_ip(ip,port)
            if judge_re:
                return "http://{0}:{1}".format(ip,port)
            else:
                return self.get_random_ip()

if __name__=="__main__":
    get_ip=GetIp()
    get_ip.get_random_ip()





# class RandomproxyMiddleware(object):
#     #动态设置ip代理
#     def process_request(self,request,spider):
#         get_ip=GetIp()
#         request.meta["proxy"]=get_ip.get_random_ip()









