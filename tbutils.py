
#tibanna utils
#



#Job result checker for WDL

import os
import sys
from tibanna.core import API
import boto3
from io import StringIO
from fabric import Connection
import sys, io
import pandas as pd
import os.path

import time



""" Post-run function to copy WDL outputs """
def tb_postrun(password="",jobid=None,username="ubuntu"):
  host="-"
  stat=""
  maxtries=20
  print(jobid)
  host,stat=tb_get_host_details(jobid=jobid)
  if stat=="terminated":
          sys.exit()
  print(f"Have an IP, Host is {host}")
  done=False
  failures=0
  while done is False:
          try:
                  print("Making connection")
                  c = Connection(host,user=username,connect_kwargs={"password": password})
                  c.put("scripts/sync_outputs.sh","/home/ubuntu/sync_outputs.sh")
                  c.put("scripts/remote_exec.template.sh","/home/ubuntu/remote_exec.sh")
                  c.sudo("bash /home/ubuntu/remote_exec.sh  ")
                  print("Adding crontab")
                  done=True
          except:
                  print("Failure")
                  print(f"Failed to connect to {host}  and transfer")
                  time.sleep(30)
                  failures=failures+1
                  if failures > maxtries:
                          print("Reached maximum number of tries, quitting")
                          break





""" List jobs """
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


""" EC2 client maker """
def get_ec2_client():
  client = boto3.client('ec2')
  #client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
  return(client)

def get_ec2_session():
  #make a boto session
  session = boto3.session.Session()
  #session = boto3.session.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
  return(session)


#Tag instance ID for billing purposes 
def tag_instance(instanceid=None,jobid=None,fundnumber=000000,client=None,logger=None,description='description',sample="samplex",project="project123",workflow="wf123"):
  if "PROJECTID" in os.environ:
        project  = str(os.environ["PROJECTID"])
  mytags=[{'Key':'Description', 'Value':description},\
    {'Key':'Project', 'Value':project},\
    {'Key':'FundNumber', 'Value':str(fundnumber)},\
    {'Key':'sample', 'Value':sample},\
    {'Key':'workflow', 'Value':workflow},\
    {'Key':'jobid', 'Value':jobid}]
  logger.info("Adding tags")
  client.create_tags(Resources=[instanceid], Tags=mytags)
  
  
 

""" EC2 Wait for instance """
def ec2_wait_for_instance(instanceid):
    waiter = client.get_waiter('instance_status_ok')
    print(f"Waiting for {instanceid}")
    waiter.wait(InstanceIds=[instanceid])
    print("instance ready")
    return(1)

""" Obtain the IP address of an instance given it's id"""
def ec2_instanceip(instanceid):
    inst=client.describe_instances(InstanceIds=[instanceid])
    ipadd=inst["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    return(ipadd)


""" KIll the instance """
def ec2_terminate_instance(instanceid):
    print("Terminating")
    response = client.terminate_instances(InstanceIds=[instanceid],DryRun=False)
    print(response)
    print("instance terminated")
