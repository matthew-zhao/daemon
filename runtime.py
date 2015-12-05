import subprocess, multiprocessing, time
import memcache, ansible, hibike
from grizzly import *
import usb
import os
<<<<<<< HEAD
import hashlib
from shutil import copyfile

#for custom name
fileName = "CustomId.txt"
fileName_old = "CustomID_Old.txt"
txt = open(fileName) 
txt_old = open(fileName_old)
idName ={} #dictionary of [custom name] : ID
=======
import datetime
>>>>>>> 6f8f68fd160db0fd86311694e394bc0f42f3b19d

# Useful motor mappings
name_to_grizzly, name_to_values, name_to_ids = {}, {}, {}
student_proc, console_proc = None, None
robot_status = 0 # a boolean for whether or not the robot is executing code

if 'HIBIKE_SIMULATOR' in os.environ and os.environ['HIBIKE_SIMULATOR'] in ['1', 'True', 'true']:
    import hibike_simulator
    h = hibike_simulator.Hibike()
else:
    h = hibike.Hibike()
connectedDevices = h.getEnumeratedDevices()
print connectedDevices
# TODO: delay should not always be 20
connectedDevices = [(device, 20) for (device, device_type) in connectedDevices]
h.subToDevices(connectedDevices)

# connect to memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port])

def get_all_data(connectedDevices):
    all_data = {}
    for t in connectedDevices:
        all_data[str(t[0])] = h.getData(t[0],"dataUpdate")
    return all_data

# Called on start of student code, finds and configures all the connected motors
def initialize_motors():
    try:
        addrs = Grizzly.get_all_ids()
    except usb.USBError:
        print("WARNING: no Grizzly Bear devices found")
        addrs = []

    # Brute force to find all
    for index in range(len(addrs)):
        # default name for motors is motor0, motor1, motor2, etc
        grizzly_motor = Grizzly(addrs[index])
        grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
        grizzly_motor.set_target(0)

        name_to_grizzly['motor' + str(index)] = grizzly_motor
        name_to_values['motor' + str(index)] = 0
        name_to_ids['motor' + str(index)] = addrs[index]

    mc.set('motor_values', name_to_values)

# Called on end of student code, sets all motor values to zero
def stop_motors():
    for name, grizzly in name_to_grizzly.iteritems():
        grizzly.set_target(0)
        name_to_values[name] = 0

    mc.set('motor_values', name_to_values)

# A process for sending the output of student code to the UI
def log_output(stream):
    #TODO: figure out a way to limit speed of sending messages, so
    # ansible is not overflowed by printing too fast
    for line in stream:
        ansible.send_message('UPDATE_CONSOLE', {
            'console_output': {
                'value': line
            }
        })

def msg_handling(msg):
    global robot_status, student_proc, console_proc
    msg_type, content = msg['header']['msg_type'], msg['content']
    if msg_type == 'execute' and not robot_status:
        student_proc = subprocess.Popen(['python', '-u', 'student_code/student_code.py'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # turns student process stdout into a stream for sending to frontend
        lines_iter = iter(student_proc.stdout.readline, b'')
        # start process for watching for student code output
        console_proc = multiprocessing.Process(target=log_output, args=(lines_iter,))
        console_proc.start()
        initialize_motors()
        robot_status= 1
    elif msg_type == 'stop' and robot_status:
        student_proc.terminate()
        console_proc.terminate()
        stop_motors()
        robot_status = 0
    elif msg_type == 'gamepad':
        mc.set('time', {'time': datetime.datetime.now()})
        mc.set('gamepad', content)

peripheral_data_last_sent = 0
def send_peripheral_data(data):
    global peripheral_data_last_sent
    # TODO: This is a hack. Should put this into a separate process
    if time.time() < peripheral_data_last_sent + 1:
        return
    peripheral_data_last_sent = time.time()

    # Send sensor data
    for device_id, value in data.items():
        ansible.send_message('UPDATE_PERIPHERAL', {
            'peripheral': {
                'name': 'sensor_{}'.format(device_id),
                'peripheralType':'SENSOR_SCALAR',
                'value': value,
                'id': device_id
                }
            })

while True:
    msg = ansible.recv()
    # Handle any incoming commands from the UI
    if msg:
        msg_handling(msg)
    
    # Send whether or not robot is executing code
    ansible.send_message('UPDATE_STATUS', {
        'status': {'value': robot_status}
    })

    # Send battery level
    ansible.send_message('UPDATE_BATTERY', {
        'battery': {
            'value': 100 # TODO: Make this not a lie
        }
    })

    # Update sensor values, and send to UI
    all_sensor_data = get_all_data(connectedDevices)
    send_peripheral_data(all_sensor_data)
    mc.set('sensor_values', all_sensor_data)

    # Send motor values to UI, if the robot is running
    if robot_status:
        name_to_value = mc.get('motor_values') or {}
        for name in name_to_value:
            grizzly = name_to_grizzly[name]
            try:
                grizzly.set_target(name_to_value[name])
            except:
                stop_motors()
            ansible.send_message('UPDATE_PERIPHERAL', {
                'peripheral': {
                    'name': name,
                    'peripheralType':'MOTOR_SCALAR',
                    'value': name_to_value[name],
                    'id': name_to_ids[name]
                }
            })
    isChanged = False
 
    hash_new = hashlib.md5(txt.read()).hexdigest() #hash for file sent by runtime
    hash_old = hashlib.md5(txt_old.read()).hexdigest() #hash for the file previously sent by runtime 
    if (hash_new == hash_old):
        isChanged = True
        txt.seek(0)
        txt_old.seek (0)
    else:
        copyfile(fileName, fileName_old) #if the files are different, update the previously sent file
        isChanged = False
        txt.seek(0)
        txt_old.seek (0)

    
    # if the file was changed, update idName
    if not isChanged:
        idName ={} #dictionary of [custom name] : ID
        totalLine = 1

        for line in txt: #count the lines in text file
            totalLine+=1

        txt.seek(0) #go back to the beginning of the file

        for x in range(1, totalLine): #add the ID and custom name to the idName dictionary
            oldId = txt.read(2)
            txt.read(2)
            newID = txt.readline()
            newID =''.join(newID.split('\n'))
            idName[newID] = oldId
    
        #print idName

    
    txt.seek(0)



    time.sleep(0.02)
