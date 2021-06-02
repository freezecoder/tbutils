
#tibanna utils
#



#Job result checker for WDL

import os
import sys
from tibanna.core import API

from io import StringIO
from fabric import Connection
import sys, io
import pandas as pd
import os.path

import time



maxtries=20

""" List jkobs """
def tb_list_jobs(n=5):
  #To change TIbanna instance set os. environ
  tb=API()
  stdout = sys.stdout
  sys.stdout = io.StringIO()
  # call module that calls print()
  tb.stat(verbose=True,n=n)
  # get output and restore sys.stdout
  output = sys.stdout.getvalue()
  sys.stdout = stdout
  df = pd.read_csv(StringIO(output),sep="\t")
  return(df)


""" Get Host details """
def tb_get_host_details(jobid=None):
  host="-"
  stat=""
  while host == "-":
    try:
      jbs=tb_list_jobs()
      jbs=jbs[jbs.jobid.str.contains(jobid)]
      print(jbs)
      host=jbs.ip.tolist()[0]
      stat=jbs.instance_status.tolist()[0]
      if stat=="terminated":
        print("No longer exists")
        break
       print(host)
       time.sleep(10)
     except:
      pass
  return(host,stat)


