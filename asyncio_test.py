import asyncio
import random
import time
import threading
from multiprocessing.pool import ThreadPool


def get_temperature_humidity():
    while True:   
        time.sleep(random.randint(1,10))
        return 10, 20


def main():
    while True:
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(get_temperature_humidity)

        #print current time
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        time.sleep(30)

        temp, hum = async_result.get()

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        print(f'Temperature: {temp} Humidity: {hum}')

if __name__ == '__main__':
    asyncio.run(main())