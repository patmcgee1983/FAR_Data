# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 19:18:29 2020

@author: fatsa
"""

import time
import SnowScraper
from datetime import datetime

# some python code that I want 
# to keep on running
counter = 1

print("========= Starting Mountain Guide =========")
while True:
     print("\n")
     print("Starting Scraper Job #"+str(counter))
     
     
     SnowScraper.scrape()    
     counter = counter + 1
     time.sleep(300)