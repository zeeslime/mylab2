from fastapi import FastAPI
import psutil
import time
import docker
import uvicorn
import uuid
from py3nvml.py3nvml import *
from cpu_data import get_cpu_data
import psycopg2
from config_db import config

app = FastAPI()

#Landing page
@app.get("/")
async def root():
    return {"Page" : "Home"}

#Docker Test Link
@app.get("/docker/{image_name:path}")
async def docker_page(image_name: str):
    """[WIP Untested]

    Args:
        image_name ([String]): [Name of docker image]
    """
    client = docker.from_env()
    print("Starting Container")
    container  = client.containers.run(image_name, detach=True)
    time.sleep(20)
    print("Stopping Container")
    container.stop()
    
#List of Process ids
@app.get("/pid")
async def pid():
    data = psutil.pids()
    return {"PID" : data}

#Overall CPU usage %
@app.get("/cpu")
async def cpu():
    data = psutil.cpu_percent()
    return {"CPU_Usage" : data}

#Currunt PID CPU usage %
@app.get("/cpu2")
async def cpu_two():
    return get_cpu_data()

#Path intake with UUID return
@app.get("/path/{path}")
async def path(path):
    """[summary]

    Args:
        path ([String]): [path to docker image]

    Returns:
        [Json]: [Returns Json with path recevied and UUID for task]
    """
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
    uuidv4 = uuid.uuid4()
    uuidv4 = str(uuidv4).replace("-","")
    #Make initial table
    # cursor.execute('''CREATE TABLE data
    #                 ( id text, path text, cpu_name text, cpu_util text, gpu_name text, gpu_peak_power text, gpu_avg_power text, gpu_peak_vram text, gpu_avg_vram text, gpu_peak_util text, gpu_avg_util text)''')
    command = f"INSERT INTO data VALUES ('{uuidv4}', '{path}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
    cursor.execute(command)
    connection.commit()
    connection.close()
    return {"Path" : path, "ID" : uuidv4}

#Nvidia-smi wrapper response
@app.get("/gpu")
async def gpu():
    """[summary]
    Return GPU data from py3nvml
    Returns:
        [String Array]: [<Device Number> : <Device Name> Power:<Power used in mW> GPU Usage : <GPU Utilization in % VRAM Usage : <VRAM Usage in B> ]
    """
    output = []
    nvmlInit()
    deviceCount = nvmlDeviceGetCount()
    for i in range(deviceCount):
        handle = nvmlDeviceGetHandleByIndex(i)
        name = nvmlDeviceGetName(handle)
        power = nvmlDeviceGetPowerUsage(handle)
        usage = nvmlDeviceGetUtilizationRates(handle)
        vram = nvmlDeviceGetMemoryInfo(handle)
        output.append(f"Device {i}: {name} Power : {power} mW GPU Usage: {usage.gpu}% VRAM Usage : {vram.used} B")
    nvmlShutdown()
    return output

@app.get("/id/{ID:path}")
async def data(ID: str):
    """[WIP Skeleton only for now]
    """
    print("HELLO MY ID IS:" + ID)
    # Look up ID in database
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM data WHERE id=:input''', {"input" : ID})
    data = cursor.fetchone()
    connection.commit()
    connection.close()

    #Return Data
    data = {
        "requestid" : data[0],
        "imagename" : data[1],
        "cpuname" : data[2],
        "cpuutilization" : data[3],
        "gpuname" : data[4],
        "gpupeakpower" : data[5],
        "gpuaveragepower" : data[6],
        "gpupeakvram" : data[7],
        "gpuaveragevram" : data[8],
        "gpupeakutilization" : data[9],
        "gpuaverageutilization" : data[10]
    }
    return data

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")