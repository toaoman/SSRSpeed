#coding:utf-8

import requests
import time
import copy
import threading
import queue
import logging

from SSRSpeed.ThreadPool.thread_pool import ThreadPool
from SSRSpeed.ThreadPool.abstract_task import AbstractTask

logger = logging.getLogger("Sub")

from config import config

wConfig = {}
try:
	wConfig = config["webPageSimulation"]
except KeyError:
	raise Exception("Web page simulation configurations not found.")

results = []
resLock = threading.Lock()
tasklist = queue.Queue(maxsize=15)

def startWebPageSimulationTest(localHost, localPort):
	logger.info("Start web page simulation test.")
	logger.info("Proxy {}:{}".format(localHost, localPort))
	proxies = {
		"http": "socks5://{}:{}".format(localHost, localPort),
		"https": "socks5://{}:{}".format(localHost, localPort)
	}
	maxThread = wConfig.get("maxThread", 4)
	urls = copy.deepcopy(wConfig.get("urls", []))
	threadPool = ThreadPool(maxThread, tasklist)
	for url in urls:
		task = WpsTask(url=url, proxies=proxies)
		tasklist.put(task)
	
	threadPool.join()


class WpsTask(AbstractTask):
	def __init__(self, *args, **kwargs):
		super(WpsTask, self).__init__(args, kwargs)
		self.url = kwargs["url"]
		self.__proxies = kwargs["proxies"]

	def execute(self):
		logger.debug("Thread {} started.Url: {}.".format(threading.current_thread().ident, self.url))
		res = {
			"url": self.url,
			"retCode": 0,
			"time": 0
		}
		try:
			startTime = time.time()
			rep = requests.get(self.url, proxies=self.__proxies, timeout=10)
			res["retCode"] = rep.status_code
			stopTime = time.time()
			res["time"] = stopTime - startTime
			logger.info("Url: {}, time used: {:.2f}s, code: {}".format(self.url, res["time"], res["retCode"]))
		except requests.exceptions.Timeout:
			logger.error("Url: {} timeout.".format(self.url))
		except requests.exceptions.SSLError:
			logger.error("SSL Error on : {}".format(self.url))
		except:
			logger.exception("")
		finally:
			pass

'''
def wpsThread(url, proxies):
	logger.debug("Thread {} started.Url: {}.".format(threading.current_thread().ident, url))
	res = {
		"url": url,
		"retCode": 0,
		"time": 0
	}
	try:
		startTime = time.time()
		rep = requests.get(url, proxies=proxies, timeout=10)
		res["retCode"] = rep.status_code
		stopTime = time.time()
		res["time"] = stopTime - startTime
		logger.info("Url: {}, time used: {}ms, code: {}".format(url, res["time"], res["retCode"]))
	except requests.exceptions.Timeout:
		logger.error("Url: {} timeout.".format(url))
	except:
		logger.exception("")
	finally:
		resLock.acquire()
		results.append(res)
		resLock.release()
'''
