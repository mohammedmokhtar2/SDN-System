# SDN Intelligent Load Balancer

A university project that builds a Software-Defined Network (SDN) capable of detecting congestion and dynamically rerouting traffic using the OpenFlow protocol.

## 🏗 System Architecture

- **Infrastructure:** Mininet (6 switches, 6 hosts, redundant topology)
- **Controller:** POX (Python-based OpenFlow controller)
- **Dashboard:** Flask web application for real-time traffic visualization

---

## 🚀 Installation

### Prerequisites

- Ubuntu 20.04 / 22.04 or Pop!\_OS
- Python 3.8+

### 1. Install Mininet & POX

```bash
# Update packages
sudo apt update && sudo apt install -y git help2man python3-pip

# Clone Mininet
git clone https://github.com/mininet/mininet.git
cd mininet
git checkout -b mininet-2.3.0 2.3.0

# (Pop!_OS only) Force installer to treat system as Ubuntu
sed -i '/Detected Linux distribution/a DIST="Ubuntu"' util/install.sh

# Install Mininet + POX + OpenFlow
./util/install.sh -a -v
```

---

## 2. Set Up the Project

```bash
# Clone this repository
git clone https://github.com/mohammedmokhtar2/SDN-System.git
cd sdn_project

# Install dependencies
pip3 install -r requirements.txt

# Symlink controller to POX
ln -s $(pwd) ~/pox/ext/sdn_project
```

---

## ⚡ Running the System (3-Terminal Workflow)

### **Terminal 1 – Controller**

```bash
~/pox/pox.py log.level --DEBUG sdn_project.controller
```

### **Terminal 2 – Mininet Topology**

```bash
sudo mn -c        # Clean previous instances
sudo python3 topology.py
```

### **Terminal 3 – Web Dashboard**

```bash
python3 app.py
```

**Dashboard:** Open → [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Testing

### Check Connectivity

```bash
h1 ping -c 3 h2
```

### Generate Congestion

```bash
iperf h1 h2
```

### Expected Behavior

- Controller logs: **“REROUTING TRAFFIC”**
- Dashboard: Load spike & status turns **red**

---

## 👥 Authors

- Mohammed Mokhtar

