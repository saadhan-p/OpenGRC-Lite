# 🛡️ OpenGRC Enterprise Transformation Master Roadmap & Execution Guide

Welcome to the **OpenGRC Enterprise Transformation Roadmap**. This document provides a step-by-step master guide to transforming OpenGRC from a basic continuous monitoring prototype into a production-grade **Continuous Controls Monitoring (CCM) & Security Posture Management (CSPM)** platform.

---

## 🎯 Executive Overview & Target Architecture

```mermaid
graph TB
    subgraph Endpoint Layer
        Agent1[Linux Host Agent]
        Agent2[macOS Host Agent]
        Agent3[Windows Host Agent]
    end
    
    subgraph Agentless Collectors
        AWS[AWS CSPM Collector]
        GH[GitHub SaaS Scanner]
    end

    subgraph Security & Ingestion Layer
        Gateway[Flask REST API + mTLS / Auth Verification]
        Queue[(Celery / Redis Queue)]
    end

    subgraph Core Engine
        Engine[Multi-Framework GRC Mapping Engine<br/>ISO 27001 | SOC 2 | NIST CSF | CIS]
        DB[(PostgreSQL Database<br/>Encrypted Audit Store)]
    end

    subgraph Real-Time & Event Dispatch
        SSE[WebSockets / SSE Event Streamer]
        Alerts[Alert Engine: Slack / Email / Webhooks]
    end

    subgraph Frontend / UI
        UI[Custom Enterprise Security Dashboard]
    end

    Agent1 -->|mTLS / HMAC Signed API| Gateway
    Agent2 -->|mTLS / HMAC Signed API| Gateway
    Agent3 -->|mTLS / HMAC Signed API| Gateway
    AWS -->|OAuth / API SDK| Gateway
    GH -->|PAT / Webhooks| Gateway

    Gateway --> Queue
    Queue --> Engine
    Engine --> DB
    Engine --> SSE
    Engine --> Alerts
    SSE --> UI
```

---

## 📅 Roadmap Overview & Progress Tracker

- [ ] **Phase 0**: Project Structuring & Environment Setup
- [ ] **Phase 1**: Zero-Trust Security & Agent Authentication Layer
- [ ] **Phase 2**: Relational Schema Redesign & Multi-Framework Engine
- [ ] **Phase 3**: Agent 2.0 - Modular Plugin Collector Architecture
- [ ] **Phase 4**: Real-Time Streaming & Async Event Pipeline
- [ ] **Phase 5**: Risk Exception & SLA Management Workflows
- [ ] **Phase 6**: Agentless Cloud & SaaS Integration Collectors
- [ ] **Phase 7**: Automated Audit Report Generation & Export Engine

---

## 🛠 Phase 0: Project Structuring & Environment Setup

### 💡 Objective
Transition from single-file scripts to a modular application directory structure, with virtual environment and dependency management.

### 📍 Where to Start
- Project Root: `/Users/saadhan/Drive/Projects/CyberSecurity/OpenGRC-Lite/`

### 📝 Step-by-Step Instructions

1. **Reorganize Repository Directory Structure**:
   ```
   OpenGRC-Lite/
   ├── app/
   │   ├── __init__.py
   │   ├── models/            # SQLAlchemy database models
   │   │   ├── __init__.py
   │   │   ├── audit.py
   │   │   ├── framework.py
   │   │   └── host.py
   │   ├── api/               # API routes & blueprints
   │   │   ├── __init__.py
   │   │   ├── agent.py
   │   │   ├── dashboard.py
   │   │   └── reports.py
   │   ├── services/          # Core GRC & business logic
   │   │   ├── __init__.py
   │   │   ├── auth_service.py
   │   │   ├── compliance_engine.py
   │   │   └── alert_service.py
   │   └── config.py          # App configuration & environment variables
   ├── agent/                 # Endpoint agent package
   │   ├── agent.py           # Main agent runner
   │   ├── config.py          # Agent local settings
   │   └── plugins/           # OS-specific check plugins
   │       ├── firewall.py
   │       ├── encryption.py
   │       ├── ssh.py
   │       └── edr.py
   ├── requirements.txt
   ├── config.env.example
   ├── server.py              # Application entry point
   └── README.md
   ```

2. **Update `requirements.txt`**:
   Add dependencies for production deployment:
   ```text
   Flask>=3.0.0
   Flask-SQLAlchemy>=3.1.0
   Flask-Migrate>=4.0.0
   PyJWT>=2.8.0
   cryptography>=41.0.0
   requests>=2.31.0
   psutil>=5.9.0
   python-dotenv>=1.0.0
   reportlab>=4.0.0
   ```

3. **Configure Environment Variables (`.env`)**:
   Create a template `.env` for secrets (`SECRET_KEY`, `JWT_SECRET`, `DATABASE_URL`).

### 🔍 Verification Criteria
- Run `python server.py` and verify all blueprints load clean without circular import errors.

### 📋 Phase 0 Checklist
- [ ] Create directory structure (`app/`, `agent/plugins/`, `app/services/`)
- [ ] Update `requirements.txt` and install dependencies
- [ ] Set up `.env` file management with `python-dotenv`

---

## 🔒 Phase 1: Zero-Trust Security & Agent Authentication Layer

### 💡 Objective
Prevent unauthorized endpoints from posting telemetry by implementing Agent Enrollment, HMAC request signing, API key verification, and Host Heartbeat monitoring.

### 📍 Files to Modify / Create
- `app/models/host.py` [NEW]
- `app/services/auth_service.py` [NEW]
- `app/api/agent.py` [MODIFY]
- `agent/agent.py` [MODIFY]

### 📝 Step-by-Step Instructions

1. **Create Host & Token Models (`app/models/host.py`)**:
   - `AgentHost`: `id`, `hostname`, `ip_address`, `os_type`, `api_key_hash`, `status` (`ONLINE`, `OFFLINE`), `last_seen`, `enrolled_at`.
   - `EnrollmentToken`: `token`, `is_used`, `created_at`, `expires_at`.

2. **Implement Handshake & Enrollment API**:
   - Endpoint `/api/v1/agent/enroll` (POST): Takes `enrollment_token` and `hostname`. Generates a unique `agent_api_key` and saves the host record. Returns the `api_key` to the agent.

3. **Implement HMAC Request Signature Verification**:
   - Every telemetry report sent by `agent.py` must include headers:
     - `X-Agent-ID`: `hostname`
     - `X-Timestamp`: UTC timestamp
     - `X-Signature`: `HMAC-SHA256(payload + timestamp, agent_api_key)`
   - In `app/api/agent.py`, write a Decorator `@require_agent_auth` that verifies timestamp freshness ($<300s$) and checks HMAC signature against the host's stored key.

4. **Heartbeat & Disconnection Monitor**:
   - Add a background daemon check that marks `AgentHost.status = 'OFFLINE'` if `last_seen` $> 5$ minutes ago.

### 🔍 Verification Criteria
- Attempt to `POST /api/report` without HMAC signature -> Returns `401 Unauthorized`.
- Enroll agent via token -> Receives API Key -> Payload signed with HMAC -> Returns `200 OK`.

### 📋 Phase 1 Checklist
- [ ] Create `AgentHost` and `EnrollmentToken` database models
- [ ] Build `/api/v1/agent/enroll` endpoint
- [ ] Implement `@require_agent_auth` HMAC verification decorator
- [ ] Update `agent.py` to store API Key and sign requests with HMAC-SHA256
- [ ] Implement background host status monitor (`ONLINE`/`OFFLINE`)

---

## 📊 Phase 2: Relational Schema Redesign & Multi-Framework Engine

### 💡 Objective
Map technical control findings to multiple compliance frameworks (ISO 27001, SOC 2, NIST CSF, CIS Benchmarks).

### 📍 Files to Modify / Create
- `app/models/framework.py` [NEW]
- `app/models/audit.py` [MODIFY]
- `app/services/compliance_engine.py` [NEW]

### 📝 Step-by-Step Instructions

1. **Design GRC Engine Schema (`app/models/framework.py`)**:
   - `Framework`: `id`, `code` (e.g., `ISO_27001_2022`, `SOC2_TYPE2`), `name`, `version`.
   - `Control`: `id`, `framework_id`, `control_code` (e.g., `A.8.20`, `CC6.6`), `title`, `description`, `category`.
   - `CheckDefinition`: `check_id` (e.g., `FIREWALL_ACTIVE`), `name`, `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
   - `ControlCheckMapping`: Junction table linking `check_id` to one or more `control_id`s across standards.

2. **Build Compliance Scoring Algorithm (`app/services/compliance_engine.py`)**:
   - Compute weighted overall score:
     $$\text{Score} = \sum (\text{Passed Checks} \times \text{Weight}) / \sum (\text{Total Checks} \times \text{Weight})$$
     (Weights: Critical = 4, High = 3, Medium = 2, Low = 1)
   - Compute breakdown score for each framework (`ISO 27001 %`, `SOC 2 %`, `NIST %`).

3. **Seed Database with Controls**:
   - Create a JSON seed file (`app/seeds/frameworks.json`) populated with initial control mappings for ISO 27001, SOC 2, and CIS Controls.

### 🔍 Verification Criteria
- Seed standard frameworks into database.
- Run test telemetry payload -> Verify score is computed per framework with weighted severities.

### 📋 Phase 2 Checklist
- [ ] Build `Framework`, `Control`, `CheckDefinition`, and `ControlCheckMapping` models
- [ ] Create database seed file for ISO 27001, SOC 2, and CIS controls
- [ ] Implement weighted compliance score calculation logic
- [ ] Expose `/api/v1/compliance/summary` endpoint returning scores per framework

---

## 🧰 Phase 3: Agent 2.0 - Modular Plugin Architecture

### 💡 Objective
Upgrade `agent.py` into a robust cross-platform system collector capable of inspecting OS firewalls, disk encryption, SSH configuration, pending updates, and active EDR software.

### 📍 Files to Modify / Create
- `agent/agent.py` [MODIFY]
- `agent/plugins/firewall.py` [NEW]
- `agent/plugins/disk_encryption.py` [NEW]
- `agent/plugins/ssh_hardening.py` [NEW]
- `agent/plugins/edr_check.py` [NEW]

### 📝 Step-by-Step Instructions

1. **Create Plugin Base Interface (`agent/plugins/base.py`)**:
   ```python
   class BaseCheckPlugin:
       check_id = "GENERIC_CHECK"
       
       def run(self) -> tuple[str, str, dict]:
           """Returns (STATUS, DETAILS_MSG, RAW_EVIDENCE)"""
           raise NotImplementedError
   ```

2. **Implement Key System Checks**:
   - **`firewall.py`**:
     - Linux: `ufw status` / `iptables -L`
     - macOS: `defaults read /Library/Preferences/com.apple.alf globalstate`
     - Windows: `netsh advfirewall show currentprofile`
   - **`disk_encryption.py`**:
     - Linux: `lsblk -o NAME,TYPE,FSTYPE` (Check for `crypto_LUKS`)
     - macOS: `fdesetup status` (Check FileVault)
     - Windows: `manage-bde -status` (Check BitLocker)
   - **`ssh_hardening.py`**:
     - Parse `/etc/ssh/sshd_config`: Validate `PermitRootLogin no`, `PasswordAuthentication no`.
   - **`edr_check.py`**:
     - Check running processes for CrowdStrike (`falcond`), SentinelOne (`sentinelctl`), Defender (`MsMpEng`), or ClamAV.

3. **Implement Dynamic Agent Execution Loop**:
   - Agent discovers available OS plugins at runtime, executes checks safely with timeouts, packages findings with raw evidence hashes (SHA-256), and transmits signed payload to backend.

### 🔍 Verification Criteria
- Run agent on Linux/macOS/Windows -> Agent dynamically detects OS, runs matching plugins, and transmits complete evidence.

### 📋 Phase 3 Checklist
- [ ] Create base plugin architecture in `agent/plugins/`
- [ ] Build multi-OS Firewall plugin
- [ ] Build Disk Encryption status plugin (FileVault, BitLocker, LUKS)
- [ ] Build SSH Hardening configuration parser
- [ ] Build EDR & Endpoint Antivirus detection plugin
- [ ] Add evidence SHA-256 hashing to check outputs

---

## ⚡ Phase 4: Real-Time Streaming & Async Pipeline

### 💡 Objective
Replace standard HTTP page refreshes with WebSockets / SSE for real-time live event streaming and fast telemetry ingestion.

### 📍 Files to Modify / Create
- `app/api/stream.py` [NEW]
- `app/services/event_bus.py` [NEW]
- `server.py` [MODIFY]

### 📝 Step-by-Step Instructions

1. **Set Up Event Stream (Server-Sent Events / WebSockets)**:
   - Implement SSE endpoint `/api/v1/stream/events` using Flask response generators.
   - When a host agent posts a payload, emit an event to all connected UI clients immediately.

2. **Add Event Ingestion Queue (Optional Redis/Celery)**:
   - For scaling telemetry ingestion, place incoming agent payloads onto an in-memory queue.
   - Worker thread processes evaluation, updates host stats, and broadcasts live event to dashboard stream.

### 🔍 Verification Criteria
- Open `/api/v1/stream/events` in browser -> Run agent -> Instantly view stream output in real-time without page reload.

### 📋 Phase 4 Checklist
- [ ] Implement Server-Sent Events (SSE) or Flask-SocketIO broadcast handler
- [ ] Connect agent payload ingestion handler to event stream
- [ ] Create live log stream subscriber endpoint for UI consumption

---

## 🚨 Phase 5: Risk Exception & SLA Management Workflows

### 💡 Objective
Handle real-world operational scenarios where failing controls require temporary business exceptions, manager approvals, and SLA tracking.

### 📍 Files to Modify / Create
- `app/models/exception.py` [NEW]
- `app/api/exceptions.py` [NEW]
- `app/services/alert_service.py` [NEW]

### 📝 Step-by-Step Instructions

1. **Design Risk Exception Model (`app/models/exception.py`)**:
   - Fields: `id`, `host_id`, `check_id`, `reason`, `business_justification`, `status` (`PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`), `approved_by`, `expires_at`.

2. **Build Exception Workflow API**:
   - `POST /api/v1/exceptions`: Submit risk acceptance request.
   - `PUT /api/v1/exceptions/<id>/approve`: Manager approval endpoint.
   - Update `compliance_engine.py`: If an active, approved exception exists for a host check, mark host check as `ACCEPTED_RISK` and do not penalize the overall score.

3. **Implement Multi-Channel Alerting Engine (`app/services/alert_service.py`)**:
   - Send webhook payloads to Slack / Microsoft Teams / PagerDuty when:
     - A `CRITICAL` check fails on any host.
     - Overall compliance score drops below threshold (e.g. $<85\%$).
     - Host goes `OFFLINE`.

### 🔍 Verification Criteria
- Trigger critical failure -> Slack notification received.
- Submit risk exception for host check -> Approved -> Compliance score recalculates automatically excluding the accepted risk.

### 📋 Phase 5 Checklist
- [ ] Create `RiskException` database model
- [ ] Build exception request and approval endpoints
- [ ] Incorporate active risk exceptions into compliance score logic
- [ ] Build Slack/Teams/Webhook notification service for critical failures

---

## ☁️ Phase 6: Agentless Cloud & SaaS Integration Collectors

### 💡 Objective
Extend OpenGRC beyond local endpoints to audit Cloud Infrastructure (AWS S3/IAM) and SaaS tools (GitHub Security).

### 📍 Files to Modify / Create
- `app/collectors/aws_collector.py` [NEW]
- `app/collectors/github_collector.py` [NEW]

### 📝 Step-by-Step Instructions

1. **AWS CSPM Collector (`app/collectors/aws_collector.py`)**:
   - Connect via `boto3` SDK:
     - Check 1: S3 bucket public access block (`s3control.get_public_access_block`).
     - Check 2: IAM root account MFA status.
     - Check 3: Security group open ingress rules (`0.0.0.0/0` on port 22/3389).

2. **GitHub SaaS Collector (`app/collectors/github_collector.py`)**:
   - Connect via GitHub REST API:
     - Check 1: Require 2FA for all organization members.
     - Check 2: Main branch protection rules enabled (require PR review).

3. **Schedule Automatic Collector Runs**:
   - Set up scheduled background tasks (e.g., using `APScheduler` or cron) to run cloud collectors every 6 hours.

### 🔍 Verification Criteria
- Trigger AWS/GitHub collector manually -> Cloud security posture checks registered into unified GRC database.

### 📋 Phase 6 Checklist
- [ ] Implement AWS S3 & IAM compliance collector using `boto3`
- [ ] Implement GitHub Organization 2FA & branch protection collector
- [ ] Add background scheduler for periodic agentless scans

---

## 📄 Phase 7: Audit Report Generation & Export Engine

### 💡 Objective
Provide auditors with one-click, formal PDF/CSV compliance report packages backed by cryptographic verification hashes.

### 📍 Files to Modify / Create
- `app/services/report_service.py` [NEW]
- `app/api/reports.py` [NEW]

### 📝 Step-by-Step Instructions

1. **Build PDF Report Generator (`app/services/report_service.py`)**:
   - Utilize `reportlab` or `weasyprint`:
     - **Header**: Organization Name, Generation Timestamp, Overall Score badge.
     - **Framework Summary Table**: Breakdown for ISO 27001, SOC 2, NIST.
     - **Control Details Table**: Status of each control check, last tested date, evidence SHA-256 hash.
     - **Active Exceptions & Risks Section**.

2. **Export API Endpoints (`app/api/reports.py`)**:
   - `GET /api/v1/reports/pdf`: Downloads formal executive PDF report.
   - `GET /api/v1/reports/csv`: Downloads raw evidence audit CSV.

### 🔍 Verification Criteria
- Call `GET /api/v1/reports/pdf` -> PDF generated cleanly with charts, tables, and verifiable evidence hashes.

### 📋 Phase 7 Checklist
- [ ] Build PDF report template using ReportLab
- [ ] Include framework scores, control statuses, and evidence hashes in report
- [ ] Create `/api/v1/reports/pdf` and `/api/v1/reports/csv` endpoints

---

## 🎯 Final Verification & Resume Highlights Summary

Once completed, your **OpenGRC Platform** will feature:
1. **Zero-Trust Agent Security**: HMAC signed telemetry with enrollment token handshake.
2. **Multi-OS Endpoint Agent**: Deep system checks for Linux, macOS, and Windows.
3. **Enterprise GRC Mapping Engine**: Cross-mapped checks across ISO 27001, SOC 2, NIST, and CIS.
4. **Real-Time Data Pipeline**: WebSockets/SSE live event streaming.
5. **Operational Workflows**: Risk exception approvals, SLA tracking, and Slack alerting.
6. **Hybrid CSPM & SaaS Audit**: Agentless scanning for AWS and GitHub.
7. **Auditor-Ready Reports**: Formal PDF/CSV report exports with cryptographic proof hashes.

Keep track of your progress by marking the checkboxes `[ ]` -> `[x]` as you complete each phase!
