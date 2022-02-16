import json
import docker


def getDockerData():
    """
        Note: Change 'gallant_gauss' to respective container name
    """
    docker_stats = {}

    # Run container 'gallant_gauss'
    client = docker.from_env()
    container = client.containers.get("gallant_gauss")

    # Acquire container id
    containerId = container.id[:12]

    # Stream current statistics of container
    status = container.stats(decode=None, stream=False)

    # Acquire CPU and memory percentage of container
    cpu_usage = calcCPUPercent(status)
    mem_usage = calcMemoryPercent(status)

    # Print container stats
    templ = "%0s %10s %12s"
    print(templ % ("CONTAINER ID", "CPU %", "MEM %"))
    print(templ % (containerId, cpu_usage, mem_usage))

    # Store container stats in json
    docker_stats["containerID"] = containerId
    docker_stats["cpuPercent"] = cpu_usage
    docker_stats["memoryPercent"] = mem_usage

    json.dumps(docker_stats)


# Calculate CPU percentage used by container
def calcCPUPercent(c_stats):
    cpu_count = len(c_stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0

    # Calculate change for cpu usage of the container in between readings
    cpu_delta = float(c_stats["cpu_stats"]["cpu_usage"]["total_usage"]) - float(c_stats["precpu_stats"]["cpu_usage"]["total_usage"])

    # Calculate change for entire system between readings
    system_delta = float(c_stats["cpu_stats"]["system_cpu_usage"]) - float(c_stats["precpu_stats"]["system_cpu_usage"])

    if system_delta > 0.0:
        cpu_percent = ((cpu_delta / system_delta) * cpu_count) * 100.0
    return round(cpu_percent, 2)


# Calculate memory percentage used by container (MEM USAGE / LIMIT)
def calcMemoryPercent(c_stats):
    # calculate memory used by container
    memory_used = c_stats["memory_stats"]["usage"] - c_stats["memory_stats"]["stats"]["cache"] + \
               c_stats["memory_stats"]["stats"]["active_file"]
    limit = c_stats['memory_stats']['limit']
    return round((memory_used / limit) * 100, 2)


if __name__ == "__main__":
    getDockerData()
