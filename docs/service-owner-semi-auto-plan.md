# Semi-Auto Service Owner Implementation Plan (ITIL-Aligned)

## 1) Scope and objective
This document operationalizes the approved approach: **PA2 — Semi-Auto Service Owner**.

### Objective
- Handle Service Owner operations across 5 prioritized services.
- Improve ticket handling speed and quality while keeping human approval gates.
- Align with ITIL practices and increase user satisfaction.

### Prioritized services (Top 5)
1. Jira
2. Tư vấn kiến trúc dịch vụ (Service Architecture)
2. Service Architecture Consulting
3. Service Desk Plus Administration
4. Zabbix Administration
5. GitLab Administration

---

## 2) Operating model

### Resolver structure
- L1: Intake, triage, standard fixes, user communication.
- L2: Advanced troubleshooting, platform configuration, complex incidents/changes.

### ITIL categories in ticket lifecycle
- Incident
- Service Request
- Problem
- Change
- Access

### Lifecycle states (recommended)
New -> Triaged -> In Progress -> Pending User/Vendor -> Resolved -> Closed

---

## 3) 30-60-90 rollout

## Day 0-30: Foundation
- Standardize taxonomy and priority matrix.
- Set baseline workflow in Service Desk Plus.
- Publish KB v1 (Top recurring issues + SOP).
- Enable human approval gates for high-risk cases.

## Day 31-60: Semi-automation
- Enable rule-based auto-triage.
- Enable response draft assistant using KB.
- Add escalation triggers near SLA breach.
- Add closure quality checklist.

## Day 61-90: Governance and optimization
- Enable KPI dashboard and review cadence.
- Implement KB governance and content ownership.
- Add CAB-lite control for service-impacting changes.
- Run continuous improvement loop (RCA -> KB/rules updates).

---

## 4) SLA policy (temporary baseline, pending final confirmation)

> Status: **OPEN** — replace with official values when available.

| Priority | First Response Target | Restore/Resolve Target | Notes |
|---|---:|---:|---|
| P1 | 15 minutes | 4h restore / 24h stable workaround | Critical business impact |
| P2 | 30 minutes | 8 business hours | High impact, limited workaround |
| P3 | 4 business hours | 2 business days | Moderate impact |
| P4 | 1 business day | 5 business days | Low impact / advisory |

---

## 5) Escalation policy (initial standard)

### Time-based escalation
- P1: escalate to L2 at T+10m if not actively handled; notify Service Owner at T+30m.
- P2: escalate to L2 when 50% of SLA consumed without clear recovery path.
- P3/P4: reminder/escalation at 80% of SLA with no user update.

### Impact-based escalation (immediate)
- Multi-team impact.
- Security/compliance exposure.
- Production data risk.
- Repeat incident pattern (>=3 similar tickets in 30 days).

### Capability-based escalation
- L1 escalates when lacking permissions or domain capability.

> Status: **OPEN** — align with existing enterprise escalation matrix when provided.

---

## 6) Service runbook expectations

## Jira
- L1: access/permission checks, project-level triage, user comms.
- L2: workflow/scheme deep fixes, integrations, advanced configs.

## Tư vấn kiến trúc dịch vụ (Service Architecture)
## Service Architecture Consulting
- L1: collect structured requirements (NFR, traffic, dependencies).
- L2: architecture recommendation with trade-offs.

## Service Desk Plus Administration
- L1: standard form/rule/role handling.
- L2: advanced workflow logic, integration-level changes.

## Zabbix Administration
- L1: alert sanity checks, host/connectivity checks.
- L2: trigger tuning, template optimization, proxy/perf issues.

## GitLab Administration
- L1: access and basic pipeline diagnostics.
- L2: runner architecture, registry/storage, advanced CI/CD issues.

---

## 7) User communication templates

### Acknowledge
"We received ticket #[TicketID] with priority [P?]. Next update by [time]."

### Progress update
"Current status: [status]. Next action: [action]. Next update ETA: [time]."

### Need more information
"Please provide: [logs/screenshots/time window/affected users] to proceed."

### Resolution/closure
"Your request/incident was resolved via [solution]. Please confirm within [x] days before auto-closure."

---

## 8) CSAT survey (default template)

> Status: **OPEN** — replace with your existing CSAT form when available.

- Q1 (1-5): Overall support satisfaction.
- Q2 (1-5): Response speed satisfaction.
- Q3 (1-5): Clarity and usefulness of resolution.
- Q4 (Yes/No): Issue fully resolved?
- Open text: Suggested improvement.

Trigger: send on ticket `Resolved`/`Closed`.

---

## 9) KPI dashboard

- SLA compliance rate
- First response time (FRT)
- Mean time to resolve (MTTR)
- Reopen rate
- First contact resolution (FCR)
- CSAT score
- Misclassification rate (ITIL type)
- KB reuse rate

Review cadence:
- Weekly: operational review.
- Monthly: trend review + action plan.
- Quarterly: policy/SLA recalibration.

---

## 10) Service Desk Plus implementation checklist

- [ ] Create/validate fields: ITIL Type, Impact, Urgency, Priority, Service.
- [ ] Configure impact/urgency -> priority matrix.
- [ ] Configure assignment rules for 5 prioritized services.
- [ ] Configure SLA policies (temporary baseline or official values).
- [ ] Configure time/impact/capability escalation rules.
- [ ] Configure user communication templates.
- [ ] Configure closure checklist and CSAT trigger.
- [ ] Configure KPI dashboard widgets/reports.
- [ ] Pilot with limited ticket categories.
- [ ] Expand to full scope after 2-week pilot review.

---

## 11) Open items tracker (to be filled from incoming MD files)

- [ ] Official SLA values for P1/P2/P3/P4.
- [ ] Existing escalation policy and owner mapping.
- [ ] Existing CSAT survey and scoring model.
- [ ] Additional compliance/audit constraints.
- [ ] Integration constraints (API limits, change windows).

When the above are provided, replace temporary defaults and freeze v1.0 operating baseline.

## 12) Reference SOP package
- Detailed copy-paste SOP for each prioritized service is available at `docs/service-owner-sop-servicedeskplus.md`.

- Production implementation artifacts are available under `production/` (machine-readable configs + validator script).
