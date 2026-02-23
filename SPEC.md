# Agentic AI for Emergency Department CT Brain Workflow
## Hospital Shah Alam - System Specification

---

## 1. Project Overview

**Project Name:** ED CT Brain Agentic AI Workflow System

**Project Type:** Multi-Agent Healthcare AI System

**Core Functionality:** An intelligent, multi-agent AI system that automates coordination across Emergency Department, Radiology, and Transport teams for CT Brain imaging. The system streamlines workflow, reduces turnaround times, improves clinical decision-making, and humanizes the patient experience through real-time tracking, predictive analytics, and enhanced communication.

**Target Users:**
- Emergency Department (ED) Physicians and Nurses
- Radiology Technicians and Radiologists
- Patient Transport Team
- Patients and Their Families

---

## 2. Problem Statement

### Current State (As-Is)
- **Long delays:** Patients may wait up to 24 hours for radiology reports
- **Unnecessary CT scans:** Lack of smart triage leads to over-utilization
- **Manual communication:** Fragmented coordination via phone/radio between ED, radiology, and transport
- **No real-time tracking:** No visibility into CT scanner availability, patient location, or scan status
- **Poor patient experience:** High anxiety, confusion, limited communication, lack of human interaction
- **Operational bottlenecks:** Delayed disposition decisions, increased length of stay

### Desired State (To-Be)
- **Automated coordination:** AI agents handle inter-team communication and task assignment
- **Real-time tracking:** Live dashboards for patient journey, scanner status, and queue management
- **Smart triage:** AI-powered clinical decision support for CT indication appropriateness
- **Reduced turnaround time:** Target <2 hours from order to preliminary report
- **Humanized experience:** VR relaxation, AI-powered FAQ, digital consent, proactive updates
- **Predictive analytics:** Wait time predictions, resource optimization, surge management

---

## 3. System Architecture

### Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ED CT Brain Workflow System                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Patient    │  │   Clinical   │  │   Resource   │          │
│  │   Agent      │  │   Agent      │  │   Agent      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────────────┬┴────────────────┬┘                   │
│                          ▼                                       │
│               ┌──────────────────────┐                           │
│               │   Orchestration      │                           │
│               │      Layer           │                           │
│               └──────────┬───────────┘                           │
│                          │                                       │
│    ┌─────────────────────┼─────────────────────┐                │
│    ▼                     ▼                     ▼                │
│ ┌────────┐         ┌───────────┐        ┌──────────┐           │
│ │   ED   │         │  Radiology│        │ Transport│           │
│ │  Team  │         │    Team   │        │   Team   │           │
│ └────────┘         └───────────┘        └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Descriptions

| Agent | Responsibility |
|-------|----------------|
| **Patient Agent** | Patient communication, status updates, FAQ, digital consent, anxiety management |
| **Clinical Agent** | Triage decision support, scan indication validation, urgency scoring, preliminary image analysis |
| **Resource Agent** | CT scanner scheduling, room availability, staff allocation, capacity forecasting |
| **Orchestration Agent** | Workflow coordination, task routing, escalation management, audit logging |

---

## 4. Functional Requirements

### 4.1 Patient Experience Module

- [ ] **AI FAQ Chatbot**: 24/7 answering patient questions about CT procedure, wait times, preparation
- [ ] **Digital Consent**: Tablet-based informed consent with multimedia explanations
- [ ] **Proactive Notifications**: SMS/WhatsApp updates on scan timing, results availability
- [ ] **VR Relaxation**: Immersive content to reduce anxiety pre-scan
- [ ] **Family Portal**: Secure web access to view patient status and receive updates

### 4.2 Clinical Decision Support Module

- [ ] **Triage Intelligence**: Validate CT indication against clinical guidelines (NINDS, AHA/ASA)
- [ ] **Urgency Scoring**: Assign priority level (Immediate/Urgent/Routine) based on clinical data
- [ ] **Appropriateness Scoring**: UCLA CT appropriateness criteria integration
- [ ] **Preliminary Analysis**: AI-assisted image QA (motion, contrast, artifact detection)

### 4.3 Workflow Coordination Module

- [ ] **Smart Queue Management**: Auto-scheduling based on urgency, prep time, scanner availability
- [ ] **Transport Coordination**: Automated transport requests with ETA predictions
- [ ] **Status Tracking**: Real-time patient journey visualization (ED → CT → Return)
- [ ] **Alert Escalation**: Configurable alerts for delays, critical findings, pending actions

### 4.4 Resource Management Module

- [ ] **Scanner Availability**: Real-time CT scanner status (Available/In-Use/Maintenance)
- [ ] **Capacity Forecasting**: Predictive models for demand surges
- [ ] **Staff Scheduling**: Integration with shift schedules for resource allocation

### 4.5 Analytics & Reporting Module

- [ ] **Dashboard**: Key metrics (TAT, scan volume, utilization, outcomes)
- [ ] **Audit Logs**: Complete audit trail for compliance and quality improvement
- [ ] **Performance Reports**: Weekly/monthly operational summaries

---

## 5. Non-Functional Requirements

### Performance
- Response time: <2 seconds for UI interactions
- Real-time updates: <5 seconds latency for status changes
- System availability: 99.5% uptime

### Security & Compliance
- **HIPAA/PHITAM Compliance**: Data encryption, access controls, audit logging
- **Data Localization**: All patient data stored within Malaysia
- **Role-Based Access**: Strict role-based permissions (ED Physician, Radiologist, Nurse, Admin)

### Integration
- **HL7 FHIR**: Standard clinical data exchange
- **PACS Integration**: DICOM worklist for image management
- **Hospital EHR**: Bidirectional integration with existing systems (MES, HIS)

---

## 6. Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | React + TypeScript, Tailwind CSS |
| **Backend API** | Node.js/Express or Python/FastAPI |
| **Database** | PostgreSQL (clinical data), Redis (caching/real-time) |
| **AI/ML** | Python, LangChain, OpenAI API (or local LLMs) |
| **Real-time** | WebSocket, Socket.io |
| **Authentication** | JWT, OAuth 2.0 |
| **Container** | Docker, Kubernetes |

---

## 7. Phased Implementation Plan

### Phase 1: Foundation (Weeks 1-4)
- System architecture design
- Database schema design
- Basic authentication and role management
- Core API endpoints

### Phase 2: Agent Development (Weeks 5-10)
- Patient Agent implementation (FAQ, notifications)
- Clinical Agent implementation (triage, urgency scoring)
- Resource Agent implementation (scanner scheduling)
- Orchestration Agent implementation

### Phase 3: Integration (Weeks 11-14)
- Real-time dashboard
- Hospital system integration (simulated)
- Testing and validation

### Phase 4: Deployment (Weeks 15-16)
- Docker containerization
- Deployment configuration
- User acceptance testing

---

## 8. Acceptance Criteria

| Feature | Success Criteria |
|---------|------------------|
| Patient FAQ | Answer 90%+ common questions correctly |
| Triage Support | >95% appropriateness score correlation with radiologist review |
| Queue Management | Reduce average TAT by 30% vs baseline |
| Real-time Tracking | Update latency <5 seconds |
| Digital Consent | Complete consent flow in <5 minutes |
| Dashboard | Load time <3 seconds, display all metrics |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Integration complexity | Use HL7 FHIR standards, create adapter layer |
| AI accuracy | Human-in-the-loop for critical decisions |
| Data privacy | Encryption at rest and in transit, audit logging |
| User adoption | Intuitive UI, phased training |
| System reliability | Graceful degradation, manual fallback |

---

## 10. Project Structure

```
ct_workflow/
├── SPEC.md
├── README.md
├── docker-compose.yml
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── patient_agent.py
│   │   │   ├── clinical_agent.py
│   │   │   ├── resource_agent.py
│   │   │   └── orchestration_agent.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── middleware/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   ├── package.json
│   └── Dockerfile
└── docs/
    └── api-documentation.md
```

---

*Document Version: 1.0*
*Created: 2026-02-21*
*For: Hospital Shah Alam Emergency Department*