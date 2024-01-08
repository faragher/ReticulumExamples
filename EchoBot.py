#! /usr/bin/python3
# EchoBot Demontration Code
# Based on various Reticulum examples

# -- PLEASE NOTE --
# EchoBot is a noisy and hacky solution to get new users
# talking on a network quickly.
# Please don't leave a copy running on the public testnet.
# One should already be running and I'm already embarrased
# at the announce spam.


import RNS
import os
import time
import LXMF

namestring = "EchoBot"
# Name in bytes for transmission purposes
namebytes = bytes(namestring,"utf-8")


# Initialize Reticulum
reticulum = RNS.Reticulum()

# Time between announces
delaytime = 3600 #seconds

# Message Response Handler
def Respond(destination, message):
  global lxm_router
  
  # Convert string to bytes below if you pass as a string
  destination_bytes = destination
  
  # Check to see if RNS knows the identity
  destination_identity = RNS.Identity.recall(destination_bytes)
  
  # If it doesn't know the identity:
  if destination_identity == None:
    basetime = time.time()
	# Request it
    RNS.Transport.request_path(destination_bytes)
	# And wait until it arrives; timeout in 30s
    while destination_identity == None and (time.time() - basetime) < 30:
      destination_identity = RNS.Identity.recall(destination_bytes)
      time.sleep(1)
  if destination_identity == None:
    print("Error: Cannot recall identity")
  # When we have the path:
  else:
    message = "Received your message: "+message
	
	# Create the destination
    lxmf_destination = RNS.Destination(
	  destination_identity,
	  RNS.Destination.OUT,
	  RNS.Destination.SINGLE,
	  "lxmf",
	  "delivery"
	  )
	  
	# NOTE: "lxmf" is the app name and "delivery" is the aspect.
	# This is what allows it to communicate with NomadNet and Sideband.
	# Otherwise these systems will filter out/not handle this message
	
	# Create the lxm object
    lxm = LXMF.LXMessage(
	  lxmf_destination, 
	  local_lxmf_destination, 
	  message, 
	  title="ACK", 
	  desired_method=LXMF.LXMessage.DIRECT
	  )
		
	# Send the message through the router
    lxm_router.handle_outbound(lxm)

def LXMDelivery(lxm):
  # The lxmessage object contains the source hash (Base Reticulum packets do not)
  # and a content which is decoded from bytes to string
  Respond(lxm.source_hash,lxm.content.decode('utf-8'))

### End routines; Initilization code

# Set user directory
userdir = os.path.expanduser("~")

# Set config directory
configdir = userdir+"/.EchoBot"

# Error handling - Make missing config directory
if not os.path.isdir(configdir):
  os.makedirs(configdir)

# Set identity path (filename)
identitypath = configdir+"/identity"

# If the file exists, load the identity
if os.path.exists(identitypath):
  ID = RNS.Identity.from_file(identitypath)
  print("Loading identity")
  
# If not, create and save a new identity
else:
  ID = RNS.Identity()
  ID.to_file(identitypath)
  print("Saving new identity")

# Create and configure LXM router
lxm_router = LXMF.LXMRouter(identity = ID, storagepath = configdir)

# Register callback
lxm_router.register_delivery_callback(LXMDelivery)

# The delivery identity takes the display name as a string
local_lxmf_destination = lxm_router.register_delivery_identity(ID,display_name=namestring)

# Print hash to terminal
print(RNS.prettyhexrep(local_lxmf_destination.hash))


# Main Loop Definition
def MainLoop():
  global namebytes, delaytime
  oldtime = 0
  while True:
    #Every delaytime seconds (and on startup)
    newtime = time.time()
    if newtime > (oldtime + delaytime):
       oldtime = newtime
	   # Announce the destination
       local_lxmf_destination.announce()
	   # And print status on the terminal
       print("Tick")
	# Remember to sleep your loops to save on processor time
    time.sleep(1)


# Execute progam
MainLoop()
