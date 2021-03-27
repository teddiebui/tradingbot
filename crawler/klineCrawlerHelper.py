import socket
import ssl
import re
from datetime import datetime
import time
import json
import pprint
import traceback
import threading


class KlineCrawlerHelper():
    
    def __init__(self):
        
        self.symbols = None 
        self.THREADS = []
        self.data = {}
        self.is_running = True
        self.error = False
        
        
    def _get_timestamp(self):
        dt = datetime.now()
        dt = dt.replace(second = 0, microsecond = 0, minute = dt.minute // 15 * 15, day = dt.day - 3)
        return str(int(dt.timestamp()*1000))
        
    def _get_new_socket(self):
        context = ssl.create_default_context()
        sock = socket.create_connection(("www.binance.com", 443))
        ssock = context.wrap_socket(sock, server_hostname="www.binance.com")
        ssock.settimeout(2)
        
        return ssock

            
    def _get_context_length(self,text):
        length = re.findall(r"Content-Length:\s*(\d+)", text, re.I)[0]
        return int(length)
        return 0
    
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
        
        while self.error == False:
        
            self.symbols = symbols
            sock = self._get_new_socket()
            self.data = {}
            self.running = True
            
            self.THREADS.append(threading.Thread(target = self._helper, args =(sock, callback)))
            self.THREADS[-1].start()
            timestamp = self._get_timestamp()
            
            
            for symbol in self.symbols[:]:
                
                request_header = [
                    "GET /api/v3/klines?symbol={}&interval={}&startTime={} HTTP/1.1\r\n".format(symbol, "15m", timestamp),
                    "Host: www.binance.com\r\n",
                    # "Connection: keep-alive\r\n",
                    "\r\n\r\n"]  
                    
                msg = "".join(request_header).encode()   
                
                sock.send(msg)

            for i in self.THREADS:
                i.join()
            if self.error == True:
                print("...retrying with another socket")
                time.sleep(1)
                continue  
            return self.data
            

            
    def _helper(self, sock, callback):
        
        
        content_length = 0
        content = ""
        delimiter = "\r\n\r\n"
        
        
        total = time.time()
        count = 0
        try:
            while self.is_running == True:
                a = time.time()
                recv = sock.recv(4048)
                content += recv.decode()
                
                if not recv:
                    print("eol")
                    return
                
                if content_length == 0:
                    header = content[:content.index(delimiter)]
                    content_length = self._get_context_length(header)
                    content = content.replace(content[:len(header)+len(delimiter)],"")
                    

                  
                if len(content) >= content_length:
                    
                    body = content[:content_length]
                    
                    content = content.replace(content[:len(body)+len(delimiter)],"")

                    data = json.loads(body)

                    if callback != None:
                        data = callback(data)
                    
                    self.data[self.symbols[count]] = data
                    
                    
                    
                    print(content_length, count+1, "/",len(self.symbols))
                    count += 1
                    content_length = 0
                
                if len(self.data) == len(self.symbols):
                    print("....crawler helper done")
                    sock.close()
                    return
        except BlockingIOError:
            print("blocking IO errror...")
            self.error = True
            return

    def stop(self):
        self.is_running = False
        
    
            
if __name__ == "__main__":
    c = CrawlerHelper()
    
    c.mainloop()