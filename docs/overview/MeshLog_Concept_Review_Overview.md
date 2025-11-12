# MeshLog System Concept Overview

## 1. Purpose and Positioning
- **Problem Space**: PrplVAS LCM deployments generate large compressed log packages that require rapid triage, deep analysis, and operational insights across WiFi mesh domains.
- **MeshLog Solution**: End-to-end platform that ingests archives, normalizes telemetry, and delivers both baseline analytics and domain-expert findings through integrated agents and rich visualizations.
- **Concept Evaluation Goal**: Demonstrate production readiness, architectural soundness, and extensibility for ongoing PrplVAS LCM initiatives.

## 2. Core Value Proposition
- **Accelerated Analysis**: Reduces manual log forensics from hours to minutes via automated parsing, classification, and analytics.
- **Domain Expertise on Demand**: Built-in agents (Steering, ACS, TPYOPT) encapsulate WiFi mesh know-how with a template path for new agents.
- **Operational Intelligence**: Provides anomaly detection, predictive insights, and trend surfacing for proactive network management.
- **Deployment Flexibility**: Dockerized stack supports dev, staging, and production modes with hybrid agent execution (integrated modules plus legacy service agents).

## 3. System Architecture Summary
- **Hierarchical Model**: Projects (log packages) → Applications (domain partitions) → Agents (specialized analyzers).
- **Two-Tier Analytics**:
  1. **Application Analysis** – log extraction, cleaning, message-type classification, and foundational statistics.
  2. **Agent Analysis** – domain reasoning, pattern recognition, and report generation for each application.
- **Hybrid Agent Runtime**: Integrated Python agents prioritized, with orchestrator-managed fallback to service-based agents when required.
- **Technology Stack**: FastAPI backend (Python 3.11+, SQLAlchemy, Celery, Redis, SQLite) and React/TypeScript frontend with Vite/MUI and Plotly visualizations.

## 4. Key Backend Components
- `ProjectAnalysisManager`, `ApplicationDataManager`, and workspace utilities coordinate uploads, discovery, and result storage.
- `AgentRegistry`, `AgentOrchestrator`, and `WorkspaceManager` handle discovery, routing, data access, and execution context for agents.
- Analytics engines (`advanced_analysis_engine`, `anomaly_detector`, `predictive_analytics`, `statistical_analyzer`) provide ML and statistical capabilities backing both tiers.

## 5. Data & Analysis Flow
```
Upload (.tar/.tar.gz/.tgz)
      ↓
Project Creation & Metadata Capture
      ↓
Package Extraction & Application Discovery
      ↓
Application Analysis (cleaning, message_type tagging, baseline analytics)
      ↓
Agent Analysis (Steering / ACS / TPYOPT / template extensions)
      ↓
Results Storage → Visualizations → Alerts & Exports
```

## 6. Agent Ecosystem Snapshot
- **Integrated Agents**: `wnc_steering`, `wnc_acs`, `wnc_tpyopt` optimized for in-process execution.
- **Template Agent**: Reference implementation for rapid domain expansion.
- **Legacy Service Mode**: Maintains compatibility with HTTP-based agents via `AgentServiceClient`.
- **Binding**: Strict application-to-agent mapping enforced by the registry and APIs.
- **Guide Alignment**: Agent documentation updates should reflect current interface signature (`analyze(log_paths, output_path, analysis_config)`).

## 7. Frontend Experience
- React dashboards surface project status, application insights, and agent outputs with live updates via WebSocket integrations.
- Visual analytics delivered through Plotly charts, filters, and export functions (PNG, PDF, HTML).
- Redux Toolkit state layer ensures consistent interaction workflows for uploads, analysis triggers, and monitoring.

## 8. Deployment & Operations
- **Container Orchestration**: `docker compose` bundles for standard, production, and agent-enhanced deployments (with override files such as `docker-compose.prod.yml`, `docker-compose.agent.yml`).
- **Scripts**: `deploy.sh`, health-check utilities, and supporting docs streamline rollout and ongoing operations.
- **Environment Configuration**: Environment variables govern agent modes, data directories, resource limits, and monitoring thresholds.
- **Scalability**: Supports horizontal worker scaling, Redis caching, and configurable resource allocations.

## 9. Security, Compliance, and Reliability
- Input validation for uploads, role-based access, JWT authentication, TLS-ready production posture.
- Container hardening practices (non-root users, scanning) and audit logging for operational traceability.
- Automated backups, disaster recovery procedures, and health checks documented across the deployment guides.

## 10. Differentiators & Readiness Indicators
- End-to-end coverage from ingestion to visualization with no external dependencies required for core agents.
- Hybrid agent architecture delivers 2–10x performance gains versus service-only models while preserving legacy compatibility.
- Comprehensive documentation set (system summary, architecture spec, agent guide, deployment manuals, gap analysis) supporting onboarding and governance.
- Remaining documentation gaps (e.g., `Application` model coverage, expanded API listings, synced agent catalogue) identified for refinement but do not block production usage.

## 11. Forward-Looking Considerations
- Prioritized enhancements include deep-learning analytics, multi-tenant support, expanded agent catalogue, real-time syslog ingestion, and microservices decomposition.
- Documentation updates recommended to harmonize specification terminology with current implementation (e.g., removal or clarification of `wnc-iot` placeholders).

## 12. Reference Materials
- `SYSTEM_SUMMARY.md` – Implementation snapshot and feature catalogue.
- `../architecture/SYSTEM_ARCHITECTURE_SPECIFICATION.md` – Detailed architectural specification (update path noted in gap analysis).
- `../architecture/AGENT_ANALYSIS_SYSTEM_GUIDE.md` – Agent orchestration and development guidance.
- `../architecture/SYSTEM_ARCHITECTURE_GAP_ANALYSIS.md` – Traceability of outstanding documentation alignment tasks.

---

**Status**: Production-ready platform validated through the MeshLog implementation; concept evaluation should focus on confirming deployment alignment, agent documentation updates, and planned extensibility.

