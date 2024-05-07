import simpy
import random

# L2 Message
class L2Message:
    def __init__(self, id, sourceMAC, destinationMAC, size, messageType):
        self.id = id
        self.sourceMAC = sourceMAC
        self.destinationMAC = destinationMAC
        self.size = size
        self.messageType = messageType

# Host process
def host(env, id, MACAddress, NIC, messages, link):
    totalBytesSent = 0
    totalBytesReceived = 0

    while True:
        yield env.timeout(random.expovariate(1))  # Exponentially distributed random time for creating message
        destIndex = random.choice([i for i in range(len(hosts)) if i != id])
        destMAC = hosts[destIndex].MACAddress
        size = random.randint(64, 1518)  # Ethernet frame size: 64-1518 bytes
        message = L2Message(len(messages) + 3, MACAddress, destMAC, size, "data")
        messages.append(message)
        totalBytesSent += size
        print(f"Host {MACAddress} created an L2 Message (size: {size})")
        env.process(link.sendMessage(message, hosts))

        yield env.timeout(0)  # Needed for event sequencing

# Link process
def link(env, id, endPoint1, endPoint2, transmissionRate, propagationDelay, errorRate):
    while True:
        message = yield linkPipe.get()
        yield env.timeout(propagationDelay)
        yield env.timeout(message.size * 8 / transmissionRate)  # Transmission time
        destHost = endPoint2 if endPoint1 == message.destinationMAC else endPoint1
        hosts[destHost].receiveL2Message(message)

# Host class
class Host:
    def __init__(self, id, MACAddress, NIC):
        self.id = id
        self.MACAddress = MACAddress
        self.NIC = NIC

    def receiveL2Message(self, message):
        print(f"Host {self.MACAddress} destroyed an L2 Message (size: {message.size})")

# Simulation setup
env = simpy.Environment()

hosts = []
links = []
messages = []
linkPipe = simpy.Store(env)

# Create hosts
hosts.append(Host(0, "MAC1", 2))
hosts.append(Host(1, "MAC2", 2))

# Create links
links.append(simpy.Process(env, link(env, 2, 0, 1, 1000000, 0, 0)))  # Transmission rate: 1Mbps

# Start host processes
for host_obj in hosts:
    env.process(host(env, host_obj.id, host_obj.MACAddress, host_obj.NIC, messages, linkPipe))

# Run simulation
env.run(until=100)

# Print statistics
print("Host 1 total bytes sent:", hosts[0].totalBytesSent)
print("Host 1 total bytes received:", hosts[0].totalBytesReceived)
print("Host 2 total bytes sent:", hosts[1].totalBytesSent)
print("Host 2 total bytes received:", hosts[1].totalBytesReceived)
