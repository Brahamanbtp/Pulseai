# ⚡ PulseAI - AI Energy & Hardware Profiler

> Intelligent hardware-aware profiling system that analyzes AI workload execution and recommends the most efficient compute backend based on performance, stability, and energy efficiency.

---

## 🚀 Overview

Modern AI workloads are typically optimized for **maximum performance**, not **maximum efficiency**.

However, real-world deployments - especially on **AI PCs, edge devices, and heterogeneous hardware systems** - require intelligent decisions about **where** an AI workload should run.

**PulseAI** is a production-style AI profiling framework that:

✅ Profiles AI workloads across hardware backends  
✅ Collects real-time system telemetry  
✅ Models efficiency & sustainability metrics  
✅ Detects execution stability  
✅ Generates hardware recommendations  
✅ Produces cryptographically verifiable experiment reports  

Instead of asking:

> *“Which hardware is fastest?”*

PulseAI answers:

> **“Which hardware executes this AI workload most efficiently?”**

---

## 🎯 Problem Statement

AI systems today face:

- Increasing energy consumption
- Inefficient hardware utilization
- Blind backend selection (CPU vs GPU)
- Lack of sustainability-aware AI execution
- No transparent benchmarking evidence

Industries and hardware vendors require tools that can **intelligently match AI workloads to compute resources**.

PulseAI addresses this gap.

---

## 🧠 Key Idea

PulseAI treats AI execution as an **observable experiment**.
```bash

AI Workload
↓
Hardware Backend
↓
Real-Time Telemetry Sampling
↓
Statistical Analysis
↓
Efficiency Modeling
↓
Backend Recommendation
```

---

## 🏗 System Architecture

```bash
pulseai/
│
├── CLI Interface
├── Experiment Orchestrator
├── Hardware Abstraction Layer
│ ├── CPU Backend
│ └── GPU Backend
│
├── Metrics Engine
│ ├── CPU Telemetry
│ ├── GPU Telemetry
│ └── Real-Time Sampler
│
├── AI Workloads
│ └── Transformer Text Inference
│
├── Analyzer
├── Recommendation Engine
├── Integrity Layer
└── Reporting System
```

---

## ⚙️ Features

### Hardware-Aware AI Profiling
- CPU / GPU backend execution
- Extensible accelerator architecture
- Vendor-neutral design

### Real-Time Telemetry
- CPU utilization monitoring
- Memory pressure tracking
- GPU utilization proxy
- Time-series sampling

### Efficiency Modeling
PulseAI evaluates:

- Throughput (tokens/sec)
- Stability score
- Energy-per-token proxy
- Efficiency score

### Intelligent Recommendation Engine
Automatically recommends optimal backend based on:

- Sustainability
- Performance
- Execution stability

### Verifiable Experiment Reports
Each experiment generates:

- JSON audit artifact
- CSV performance summary
- Integrity fingerprint (SHA256)

Tampering becomes detectable.

---

## 🤖 AI Workload

PulseAI profiles real transformer inference:

- Model: **DistilGPT2**
- Task: Text generation
- Metric: Tokens generated
- Deterministic execution

This represents modern LLM inference workloads.

---

## 📊 Example Output

```bash
========== PulseAI Recommendation ==========
Recommended Backend : CPU
Mode : sustainability
Efficiency Score : 0.90
Stability Score : 0.98
Report Saved : reports/pulseai-xxxx.json
```

---

## 🧪 Experimental Results
```bash
| Run | Throughput | Efficiency | Stability |
|----|----|----|----|
| Run 1 | 53.95 tok/s | 0.84 | 0.94 |
| Run 2 | 55.16 tok/s | 0.90 | 0.98 |
```
PulseAI identified CPU execution as the most sustainable backend in the tested environment.

---

## 🛠 Installation

### 1️. Clone Repository

```bash
git clone https://github.com/<your-username>/PulseAI.git
cd PulseAI
```
### 2️. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```
### 3️. Install Dependencies
```bash
pip install torch transformers psutil python-dotenv
```
### ▶️ Running PulseAI
Run Single Backend Profiling
```bash
python -m pulseai.cli run --backend cpu
```
Cross Backend Comparison
```bash
python -m pulseai.cli compare --backends cpu gpu
```
### 📁 Generated Reports
```bash
reports/
├── pulseai-xxxx.json
└── pulseai-xxxx.csv
```

#### Reports contain:

- experiment metadata

- efficiency metrics

- backend recommendation

- integrity hash
---

### 🔐 Integrity Verification

#### Each report includes:
```bash
"integrity": {
  "hash_algorithm": "sha256",
  "fingerprint": "..."
}
```

#### Ensuring experiment authenticity.
---

### 🌱 Sustainable AI Focus

#### PulseAI promotes:

- Energy-aware inference

- Efficient hardware utilization

- Responsible AI deployment

- Edge & AI PC optimization
---

### 🧩 Extensibility

#### Future backends can be added easily:

- `AMDNPUBackend`
- `EdgeAcceleratorBackend`
- `ROCmBackend`
- `FPGABackend`

#### No redesign required.
---

### 🎯 AMD Slingshot Alignment

#### PulseAI directly supports:

- Heterogeneous compute optimization
- AI PC ecosystem
- Edge AI deployment
- Sustainable AI execution
- Hardware-aware AI workloads
---

### 🚀 Future Work

- Native AMD ROCm telemetry

- NPU backend integration

- Power sensor integration

- Multi-node profiling

- Auto workload scheduling
---

### 👨‍💻 Author

#### Pranay Sharma

#### AI Systems & Intelligent Infrastructure Enthusiast
---

### 📜 License

MIT License