import socket
import ssl
import threading
import re
from datetime import datetime
import time
import json
import queue


class KlineCrawlerHelper:
    
    def __init__(self, symbols):
        
        self.symbols = symbols
        self.THREADS = []
        self.data = {}
        self._data = []
        self.q = queue.Queue()
        
 
        self.count = 0
        self.sock = self._get_new_socket()
        self.is_running = True
        
    def _get_timestamp(self):
        dt = datetime.now()
        dt = dt.replace(second = 0, microsecond = 0, minute = dt.minute // 15 * 15)
        print(dt)
        return str(int(dt.timestamp()*1000))
        
    def _get_new_socket(self):
        context = ssl.create_default_context()
        sock = socket.create_connection(("www.binance.com", 443))
        ssock = context.wrap_socket(sock, server_hostname="www.binance.com")
        ssock.settimeout(1)
        
        return ssock
    
    def _helper(self,sock):
        content_length = 0
        header_length = 0
        body_length = 0
        data = ""
        content = ""
        delimiter = "\r\n\r\n"
        
        try:
            total = time.time()
            while self.is_running == True:
                a = time.time()
                recv = sock.recv(4048)
                content += recv.decode()
                
                print(recv)
                continue
                

                content_length = self._get_context_length(content)
                    

                header = content[:content.index(delimiter)]
                # print(header.encode())
                # print("\n")
                
                content = content.replace(content[:len(header)+4],"")
                
                
                
                
                if len(content) >= content_length:
                    body = content[:content_length][1:-1]
                    data += ", " + body
                    content = content.replace(body,"")
                    done_time = time.time() - a
                    print("inside time: ", done_time)
                    continue
                    # self._data.append(json.loads(body)[0])
                    # json_time = time.time()
                    # self.q.put(json.loads(body)[0])
                    # json_time = time.time() - json_time
                    
                    
                    
                    # print(body)
                    print("inside time: ", done_time, "json_time: ", json_time)
                  
                
        except socket.timeout:
            print("timeout")
            total = time.time() - total
            print(data)
            data = "[" + data[1:] + "]"
            self._data = json.loads(data)

            print("total time: ", total)
            
            self.is_running = False
            
            # print(content)
            
            
            # for i in set(re.findall(r"(\[\[.*?\]\])", content)):
                # self.data.extend(json.loads(i))
            
            # for i in self.data:
                # print(i)
                
            # print("finished in: ", b - a)
            # print("total: ", len(self.data))
            # print("total symbol: ", len(self.symbols))
            # print(content)
            

        return
            
    def _get_context_length(self,text):
        length = re.findall(r"Content-Length: (\d+)", text)[0]
        return int(length)
    
    def _get_header(self, text):
    
        content = re.findall(r"(.*?)\r\n\r\n", text, re.S)
        return content
        
    def _get_body(self, text):

        content = re.findall(r"(\[\[.*?\]\])", text)[0]
        return content
    
    def mainloop(self):
        import time

        thread = threading.Thread(target = self._helper, args =(self.sock,))
        # thread.start()
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
            
        content_length = 0
        header_length = 0
        body_length = 0
        data = ""
        content = ""
        delimiter = "\r\n\r\n"
            
        try:
            total = time.time()
            while self.is_running == True:
                a = time.time()
                recv = self.sock.recv(4048)
                content += recv.decode()
                
                

                content_length = self._get_context_length(content)
                    

                header = content[:content.index(delimiter)]
                # print(header.encode())
                # print("\n")
                
                content = content.replace(content[:len(header)+4],"")
                
                
                
                
                if len(content) >= content_length:
                    body = content[:content_length][1:-1]
                    data += ", " + body
                    content = content.replace(body,"")
                    done_time = time.time() - a
                    print("inside time: ", done_time)
                    continue
                    # self._data.append(json.loads(body)[0])
                    # json_time = time.time()
                    # self.q.put(json.loads(body)[0])
                    # json_time = time.time() - json_time
                    
                    
                    
                    # print(body)
                    print("inside time: ", done_time, "json_time: ", json_time)
                  
                
        except socket.timeout:
            print("timeout")
            total = time.time() - total
            print(data)
            data = "[" + data[1:] + "]"
            self._data = json.loads(data)

            print("total time: ", total)      
            self.sock.close()
            return self._data

    def stop(self):
        self.is_running = False
            
if __name__ == "__main__":
    c = CrawlerHelper()
    
    c.mainloop()