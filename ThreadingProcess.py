#! /bin/python3

# Object List and Threading demo
# Good for explicit control over transmissions
# No actual Reticulum action in this version

import time
import threading

DataLink = None #This would contain a Reticulum link for resource transfer
ObjectList = []
ShouldRun = True

class ObjectOfInterest:
  ObjName = "Undefined"
  ObjClass = "Undefined"
  ObjSerial = 0
  
  def __init__(self,N, C, S):
    self.ObjName = N
    self.ObjClass = C
    self.ObjSerial = S
    

def PrintOOI(OOI):
  print(OOI.ObjName+" - "+OOI.ObjClass+". SN:"+str(OOI.ObjSerial))
  
def ProcessOOI(ReticulumLink, OOI):
  #This simulates a five second transmission that would otherwise block processing
  print("Processing SN:"+str(OOI.ObjSerial))
  time.sleep(5)
  PrintOOI(OOI)
  print("Processing complete.")
  
def ProcessLoop(ReticulumLink, ListOfObjects):
  #This thread will not terminate on its own or when the parent terminates (for some reason)
  #The global ShouldRun is a master kill switch
  global ShouldRun
  while(ShouldRun):
    if len(ListOfObjects) > 0:
      ProcessOOI(ReticulumLink,ListOfObjects.pop(0))
    time.sleep(1)
  
def MainLoop():
  StartTime = time.time()
  global ShouldRun
  LoopNum = 0
  ProcessingThread = threading.Thread(target=ProcessLoop,args=(DataLink,ObjectList,))
  ProcessingThread.start()
  while(ShouldRun):  
    DeltaTime = time.time() - StartTime
    if DeltaTime > 30:
      ShouldRun = False
      print("Terminating - Time elapsed")
    else:
      print("Loop Number: "+str(LoopNum))
      LoopNum = LoopNum + 1
      time.sleep(1)
  print("Loops should be approximately 29 - Significantly less indicates a blocking ProcessOOI")
  print("OOI processed should be three.")
  
  
#Initialization

ObjectList.append(ObjectOfInterest("Testy","McTestface",1))
ObjectList.append(ObjectOfInterest("Foo","Bar",9))
ObjectList[1].ObjSerial = 2 #oops! Change that

#As an object
WorkingObject = ObjectOfInterest("Last","Test",4)
WorkingObject.ObjName = "Doing this"
WorkingObject.ObjClass = "The hard way"
WorkingObject.ObjSerial = 3
ObjectList.append(WorkingObject)

#Go
MainLoop()



