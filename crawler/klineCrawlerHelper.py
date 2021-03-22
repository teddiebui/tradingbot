import socket
import ssl
import threading
import re
from datetime import datetime
import time
import json
import queue
import pprint
import traceback


class KlineCrawlerHelper(threading.Thread):
    
    def __init__(self):
        
        self.symbols = None 
        self.THREADS = []
        self.data = {}
        self._data = []
        self.q = queue.Queue()
        
 
        self.count = 0
        self.sock = self._get_new_socket()
        self.is_running = True
        
        threading.Thread.__init__(self)
        
    def _get_timestamp(self):
        dt = datetime.now()
        dt = dt.replace(second = 0, microsecond = 0, minute = dt.minute // 15 * 15, day = dt.day - 3)
        print(dt)
        return str(int(dt.timestamp()*1000))
        
    def _get_new_socket(self):
        context = ssl.create_default_context()
        sock = socket.create_connection(("www.binance.com", 443))
        ssock = context.wrap_socket(sock, server_hostname="www.binance.com")
        ssock.settimeout(0.75)
        
        return ssock

            
    def _get_context_length(self,text):
        length = re.findall(r"Content-Length:\s*(\d+)", text, re.I)[0]
        return int(length)
    
    def _get_header(self, text):
    
        content = re.findall(r"(.*?)\r\n\r\n", text, re.S)
        return content
        
    def _get_body(self, text):

        content = re.findall(r"(\[\[.*?\]\])", text)[0]
        return content
    
    def run(self):
        print("still not have function yet...")
        

    def mainloop(self, symbols, callback = None):
        import time
        
        self.symbols = symbols
        thread = threading.Thread(target = self._helper, args =(self.sock, callback))
        thread.start()
        self.THREADS.append(thread)
        
        timestamp = self._get_timestamp()
        
        for symbol in self.symbols[:]:
            request_header = [
                "GET /api/v3/klines?symbol={}&interval={}&startTime={} HTTP/1.1\r\n".format(symbol, "15m", timestamp),
                "Host: www.binance.com\r\n",
                "Connection: keep-alive\r\n",
                "\r\n\r\n"]
                
            msg = "".join(request_header).encode()
            
            self.sock.send(msg)
        
        thread.join()
        return self.data

            
        # content_length = 0
        # header_length = 0
        # body_length = 0
        # data = ""
        # content = ""
        # delimiter = "\r\n\r\n"
            
        # try:
            # total = time.time()
            # while self.is_running == True:
                # a = time.time()

                # recv = self.sock.recv(4048)
                # content += recv.decode()
                
                # print(len(recv))
                # continue
                
                

                # content_length = self._get_context_length(content)

                # header = content[:content.index(delimiter)]
                # # print(header.encode())
                # # print("\n")
                
                # content = content.replace(content[:len(header)+4],"")
                
                
                
                
                # if len(content) >= content_length:
                    # body = content[:content_length][1:-1]
                    # data += ", " + body
                    # content = content.replace(body,"")
                    # done_time = time.time() - a
                    # # # print("inside time: ", done_time)
                    # # json_time = time.time()
                    # # self._data.append(json.loads(body)[0])
                    
                    # # json_time = time.time() - json_time
                    
                    # # # print(body)
                    # # print("inside time: ", done_time, "json_time: ", json_time)
                  
                
        # except socket.timeout:
            # print("timeout")
            # total = time.time() - total
            # # pprint.pprint(data)
            # data = "[" + data[1:] + "]"
            # print("total time: ", total)      
            # self.sock.close()
            # return self._data
            
    def _helper(self, sock, callback):
        
        content_length = 0
        
        data = ""
        content = ""
        delimiter = "\r\n\r\n"
        
        count = 0
        total = time.time()
        while self.is_running == True:
            a = time.time()
            recv = sock.recv(4048)
            content += recv.decode()
            
            if content_length == 0:
                content_length = self._get_context_length(content)
                header = content[:content.index(delimiter)]
                content = content.replace(content[:len(header)+len(delimiter)],"")

              
            if len(content) >= content_length:
                body = content[:content_length]
                # print(body)
                
                #call callback to do something
                data = json.loads(body)
                
                if callback != None:
                    data = callback(data)
                
                self.data[self.symbols[count]] = data
                # content = content.replace(body,"")
                # done_time = time.time() - a
                # print("done time: ", done_time)
                print(content_length, count+1, "/",len(self.symbols))
                count += 1
                content_length = 0
                
                
                

            if len(self.data) == len(self.symbols):
                print("....crawler helper done")
                sock.close()
                return

    def stop(self):
        self.is_running = False
        
    
            
if __name__ == "__main__":
    c = CrawlerHelper()
    
    c.mainloop()