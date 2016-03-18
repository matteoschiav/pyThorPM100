"""Simple interface to the Thorlabs PM100D power meter"""

from __future__ import division,print_function

import os

class DriverError:
   pass

class NoDevice:
   pass

class IOError:
   pass

class pm100d:
   def __init__(self):
      # find the file associated to the first PM100 device
      self.cntDev = '/dev/usbtmc0'
      try:
         self.cntFILE = os.open(self.cntDev,os.O_RDONLY)
      except:
         raise DriverError
      self.readLength = 4000
      devs = os.read(self.cntFILE,self.readLength)
      devs = devs.decode('utf-8')
      devs = devs.strip().split('\n')
      devs = devs[1:]
      os.close(self.cntFILE)
      # select the first PM100D found
      # TODO: allow the presence of multiple PM100D devices
      self.dev = ''
      if len(devs)>0:
         for l in devs:
            l = l.split('\t')
            if l[1]=='Thorlabs' and l[2]=='PM100D':
               self.dev = '/dev/usbtmc'+l[0][2]
               break
      if self.dev=='':
         raise NoDevice
      try:
         self.devFILE = os.open(self.dev,os.O_RDWR)
      except:
         raise NoDevice

   def __del__(self):
      os.close(self.devFILE)

   def __read(self):
      try:
         data = os.read(self.devFILE,self.readLength)
         return data
      except:
         raise IOError

   def __write(self,command):
      try:
         bytesCmd = str.encode(command)
         length = os.write(self.devFILE,bytesCmd)
         if length != len(bytesCmd):
            raise IOError
      except:
         raise IOError

   def __ask(self,command):
      self.__write(command)
      return self.__read()
         
   def identify(self):
      resp = self.__ask('*IDN?')
      resp = resp.decode("utf-8").strip()
      return resp
	
   def read(self):
      """Start new measurement and read data [W]"""
      resp = self.__ask('READ?')
      resp = resp.decode("utf-8").strip()
      resp = float(resp)
      return resp
