# Software Requirements Specification

## Intelligent Energy Management System for Buildings in Kenya

Version: 1.0  
Date: 3 April 2026  
Status: Draft for Requirements Baseline

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) defines the functional, non-functional, interface, and data requirements for an Intelligent Energy Management System (EMS) intended for commercial buildings in Kenya. The document is written to support solution design, implementation, testing, deployment, procurement, and operational acceptance.

The EMS shall collect real-time electrical and environmental data from smart meters and IoT sensors, transform that data into operational intelligence, present insights through dashboards and reports, and support automated or operator-approved control actions that reduce energy waste and operating cost.

This document is intended for developers, system architects, quality assurance engineers, UI/UX designers, DevOps engineers, facility managers, project managers, and customer stakeholders.

### 1.2 Scope
The Intelligent EMS is a building-level and multi-site platform that provides continuous monitoring, analytics, alerting, reporting, and optional automated control of electrical loads. The system shall support commercial buildings, hotels, and supermarkets with a focus on Kenyan operating conditions, including variable grid quality, mixed connectivity environments, and cost sensitivity.

The EMS shall:

1. Acquire telemetry from smart meters, submeters, and IoT sensors.
2. Process incoming data into validated, time-stamped measurements.
3. Detect abnormal consumption, poor power quality, and device communication failures.
4. Provide real-time and historical dashboards for facility managers and decision-makers.
5. Generate reports, recommendations, forecasts, and audit trails.
6. Support configurable alerts and optional automated control of selected loads.
7. Scale from a single building to a portfolio of buildings.

The EMS is not intended to replace utility billing systems, electrical protection relays, or a full building management system (BMS), though it may integrate with such systems.

### 1.3 Definitions, Acronyms, and Abbreviations
EMS: Energy Management System.  
IoT: Internet of Things.  
SRS: Software Requirements Specification.  
BMS: Building Management System.  
API: Application Programming Interface.  
RBAC: Role-Based Access Control.  
MQTT: Message Queuing Telemetry Transport.  
HTTP: Hypertext Transfer Protocol.  
HTTPS: HTTP over TLS.  
TLS: Transport Layer Security.  
kWh: Kilowatt-hour.  
kW: Kilowatt.  
PF: Power Factor.  
SCADA: Supervisory Control and Data Acquisition.  
RPO: Recovery Point Objective.  
RTO: Recovery Time Objective.  
SLA: Service Level Agreement.  
Time-series data: Measurements indexed primarily by timestamp.  
Load control: Commanded switching, curtailment, or scheduling of electrical loads.  
Anomaly: A measured or inferred condition that deviates from expected operating behavior.

### 1.4 References
1. IEEE 830, Recommended Practice for Software Requirements Specifications.
2. ISO/IEC/IEEE 29148, Systems and software engineering, Life cycle processes, Requirements engineering.
3. MQTT Version 3.1.1 or later.
4. HTTPS/TLS industry best practices for secure API communication.
5. Kenyan Data Protection Act, 2019.
6. Kenyan Energy Act, 2019.
7. Applicable utility, safety, and electrical installation standards adopted by the customer site.

### 1.5 Overview
Section 2 describes the operating context, users, and constraints. Section 3 defines system features and functional requirements. Section 4 specifies external interfaces. Section 5 defines non-functional requirements. Section 6 defines data requirements. Section 7 provides textual system models. Section 8 defines acceptance criteria.

## 2. Overall Description

### 2.1 Product Perspective
The EMS is a modular platform positioned between field devices and human or automated decision-making.

At the edge, sensors and smart meters measure electrical parameters such as voltage, current, active power, reactive power, apparent power, power factor, frequency, and energy consumption. These measurements are transmitted to the platform through gateways or direct network interfaces.

At the platform layer, the EMS validates, stores, analyzes, and visualizes the data. The analytics layer derives trends, anomalies, recommendations, and forecasts. The control layer issues operator-approved or policy-driven actions to controllable loads where such integration is enabled.

At the business layer, the system supports operational optimization, cost reduction, maintenance planning, and management reporting.

### 2.2 Product Functions
The EMS shall provide the following high-level functions:

1. Device onboarding, configuration, and health monitoring.
2. Real-time telemetry ingestion and validation.
3. Historical storage and retrieval of time-series data.
4. Dashboard visualization of building, floor, feeder, meter, and device performance.
5. Alert generation for threshold violations, anomalies, outages, and communication faults.
6. Reporting, trend analysis, baseline comparison, and forecasting.
7. User and role management with secure access control.
8. Optional automation and manual control of eligible loads.
9. Audit logging for user and system actions.
10. Multi-building aggregation for portfolio-level monitoring.

### 2.3 User Classes and Characteristics
Facility Managers:
Primary operational users responsible for monitoring consumption, reviewing alerts, analyzing trends, and approving corrective actions. They require intuitive dashboards, site-level drill-down, and actionable recommendations.

Building Owners and Management:
Decision-makers who require summary dashboards, savings reports, financial insights, and compliance-oriented evidence. They interact less frequently than facility managers and prioritize concise KPI visibility.

Technicians and Engineers:
Technical users responsible for device setup, troubleshooting, calibration checks, integration support, and control policy configuration. They require diagnostic data, communication status, event logs, and configuration interfaces.

System Administrators:
Users responsible for account provisioning, RBAC, tenant configuration, security settings, and integration management.

### 2.4 Operating Environment
The EMS shall operate in the following environment:

1. Edge hardware including smart meters, submeters, current transformers, power quality meters, relays, gateways, and environmental sensors.
2. Site networks including Ethernet, Wi-Fi, cellular, or mixed-connectivity links.
3. Cloud-hosted or hybrid application infrastructure.
4. Web browser clients on current versions of Chrome, Edge, Firefox, and Safari.
5. Mobile-responsive web interface for smartphones and tablets.
6. Backend services running on Linux-based server environments or managed cloud services.
7. Datastores supporting both time-series and transactional data.

### 2.5 Design and Implementation Constraints
1. The system shall support intermittent connectivity between building sites and the central platform.
2. The system shall support heterogeneous field devices from multiple vendors, subject to supported protocol adapters.
3. Control features shall be disabled by default and enabled only for approved devices and workflows.
4. The system shall retain timestamp accuracy across time zones, daylight-saving offsets where relevant, and clock drift scenarios.
5. The system shall comply with customer security policies and Kenyan data protection obligations for personally identifiable information where applicable.
6. The system shall not require constant high-bandwidth connectivity for basic monitoring operation.
7. The solution shall allow deployment either as single-tenant or multi-tenant depending on customer procurement model.

### 2.6 Assumptions and Dependencies
1. Customer sites shall provide safe and lawful access to metering points and electrical panels.
2. Supported sensors and meters shall be installed and calibrated according to manufacturer specifications.
3. Reliable device identification metadata shall be available during commissioning.
4. Network connectivity, whether direct or gateway-based, shall be available at least periodically for data synchronization.
5. If automation is enabled, the customer shall define approved control targets, override rules, safety limits, and operating schedules.
6. External systems such as BMS, ERP, or utility portals may have separate licensing, availability, and interface limits.

## 3. System Features

### 3.1 Feature: Real-Time Energy Monitoring
Description: The system provides near-real-time visibility into electrical consumption and power quality metrics across buildings, zones, feeders, and devices.  
Priority: High

Functional Requirements:

FR-1. The system shall display current values for voltage, current, active power, reactive power, apparent power, frequency, power factor, and cumulative energy for each supported device.

FR-2. The system shall refresh real-time dashboard values within 10 seconds of receipt of new telemetry under normal operating conditions.

FR-3. The system shall support hierarchical views for portfolio, building, floor, area, feeder, and meter where such asset mapping is configured.

FR-4. The system shall present telemetry timestamps in local site time and preserve the original UTC timestamp in storage.

FR-5. The system shall indicate device communication state as online, degraded, offline, or unknown.

FR-6. The system shall allow users to filter monitored data by site, date range, asset type, and device.

FR-7. The system shall display summary KPIs including total energy consumption, peak demand, average power factor, and estimated cost for the selected scope.

### 3.2 Feature: Data Ingestion from IoT Devices
Description: The system ingests telemetry and status data from smart meters, gateways, and sensors using supported industrial and web protocols.  
Priority: High

Functional Requirements:

FR-8. The system shall ingest measurements from supported devices using MQTT, HTTP/HTTPS, or protocol adapters defined during integration.

FR-9. The system shall validate each telemetry record for required fields including device identifier, timestamp, metric type, and measurement value.

FR-10. The system shall reject or quarantine malformed telemetry records and log the rejection reason.

FR-11. The system shall support configurable device sampling intervals from 1 second to 15 minutes, subject to device capability.

FR-12. The system shall deduplicate repeated telemetry messages using a deterministic rule based on device identifier, metric, timestamp, and message identifier where available.

FR-13. The system shall buffer inbound telemetry during temporary downstream outages and process buffered records when service is restored.

FR-14. The system shall maintain a device registry containing device type, location, protocol, commissioning status, and last communication timestamp.

FR-15. The system shall generate a communication fault event when a device fails to report within its configured heartbeat threshold.

### 3.3 Feature: Dashboard Visualization
Description: The system provides role-appropriate dashboards for operational and management decision-making.  
Priority: High

Functional Requirements:

FR-16. The system shall provide a portfolio dashboard summarizing total consumption, demand, alerts, and savings indicators across all authorized sites.

FR-17. The system shall provide a site dashboard showing live load, historical trends, power quality indicators, and active alerts.

FR-18. The system shall provide interactive charts for hourly, daily, weekly, and monthly trends.

FR-19. The system shall allow drill-down from aggregate views to device-level details.

FR-20. The system shall allow users to export dashboard data in CSV and PDF formats.

FR-21. The system shall allow users to configure dashboard widgets based on role and permissions.

FR-22. The system shall visually distinguish normal, warning, and critical states using configurable thresholds.

### 3.4 Feature: Alerts and Anomaly Detection
Description: The system identifies abnormal events and notifies relevant users.  
Priority: High

Functional Requirements:

FR-23. The system shall support threshold-based alerts for overvoltage, undervoltage, overcurrent, poor power factor, excessive consumption, demand spikes, and communication loss.

FR-24. The system shall support rule-based anomaly detection using configurable baselines such as historical average, schedule-based expectation, or peer comparison.

FR-25. The system shall allow future extension to statistical or machine learning anomaly models without changing the user-facing alert workflow.

FR-26. The system shall classify alert severity as informational, warning, high, or critical.

FR-27. The system shall notify users through in-app alerts and optionally through email, SMS, or third-party messaging integrations if enabled.

FR-28. The system shall maintain alert lifecycle states including open, acknowledged, assigned, resolved, and closed.

FR-29. The system shall record the triggering metric, threshold or model condition, timestamp, impacted asset, and resolution notes for each alert.

FR-30. The system shall suppress duplicate alert notifications for the same active incident within a configurable suppression window.

### 3.5 Feature: Reporting and Analytics
Description: The system transforms telemetry into insights for operational, financial, and technical analysis.  
Priority: High

Functional Requirements:

FR-31. The system shall generate scheduled and on-demand reports for energy consumption, peak demand, cost estimates, power factor performance, and alert history.

FR-32. The system shall allow report filtering by building, area, device group, and reporting period.

FR-33. The system shall compute comparisons against prior periods and configured baselines.

FR-34. The system shall provide estimated energy cost calculations using configurable tariff structures.

FR-35. The system shall provide forecast outputs for short-term demand and consumption using configurable forecast horizons.

FR-36. The system shall provide recommendations for energy optimization based on detected patterns, thresholds, or configured policies.

FR-37. The system shall retain a history of generated reports and allow authorized users to retrieve them.

### 3.6 Feature: User Management
Description: The system controls access and user accountability through identity and authorization functions.  
Priority: High

Functional Requirements:

FR-38. The system shall require authenticated access for all non-public functions.

FR-39. The system shall support RBAC with at least the roles of System Administrator, Facility Manager, Technician, and Executive Viewer.

FR-40. The system shall allow administrators to create, deactivate, and assign users to one or more buildings or portfolios.

FR-41. The system shall enforce permission checks for dashboard access, report generation, device management, and control actions.

FR-42. The system shall record audit logs for login, logout, password reset, role change, configuration update, and control action events.

FR-43. The system shall support configurable password policies or external identity provider integration where required by the customer.

### 3.7 Feature: Automation and Control System
Description: The system supports manual and policy-driven control of approved loads to reduce waste while preserving safety and operational continuity.  
Priority: Medium

Functional Requirements:

FR-44. The system shall support manual control commands for approved controllable devices, including on, off, schedule enable, and setpoint or mode changes where supported.

FR-45. The system shall require explicit user authorization and an audit trail for manual control actions.

FR-46. The system shall support rule-based automation using schedules, thresholds, occupancy assumptions, tariff periods, or demand-limiting policies.

FR-47. The system shall allow each automation rule to be enabled, disabled, versioned, and assigned to specific assets.

FR-48. The system shall support fail-safe behavior such that communication failure or system restart shall not issue unintended control commands.

FR-49. The system shall support manual override of automated actions by authorized users.

FR-50. The system shall prevent control actions on assets marked as safety-critical or manually locked out.

FR-51. The system shall log each control command, command issuer, target device, timestamp, command result, and any acknowledgment returned by the device.

### 3.8 Feature: Device Commissioning and Configuration
Description: The system supports onboarding and lifecycle management of devices and sites.  
Priority: Medium

Functional Requirements:

FR-52. The system shall allow authorized users to register a device with identifier, type, protocol, site, location, metric map, and heartbeat interval.

FR-53. The system shall validate uniqueness of device identifiers within a tenant.

FR-54. The system shall allow authorized users to test device connectivity during commissioning.

FR-55. The system shall maintain configuration history for device and site metadata changes.

FR-56. The system shall allow decommissioned devices to be retired without deleting historical data.

### 3.9 Feature: Multi-Building Portfolio Management
Description: The system supports centralized oversight across multiple buildings.  
Priority: Medium

Functional Requirements:

FR-57. The system shall support logical separation of data by tenant, building, and site.

FR-58. The system shall aggregate KPIs across all buildings visible to the logged-in user.

FR-59. The system shall allow comparison of performance across buildings using normalized indicators where building metadata is available.

FR-60. The system shall allow site-specific tariffs, thresholds, working schedules, and alert routing policies.

## 4. External Interface Requirements

### 4.1 User Interfaces
UI-1. The system shall provide a responsive web interface optimized for desktop, tablet, and mobile browser usage.

UI-2. The system shall provide dashboards for operational users and summary KPI views for management users.

UI-3. The system shall provide data tables, trend charts, alert panels, and report views with filtering and export functions.

UI-4. The system shall provide forms for device setup, threshold configuration, schedule definition, and user administration.

UI-5. The system shall provide confirmation dialogs for control actions and destructive administrative actions.

UI-6. The system shall expose timestamps, units of measure, and status indicators clearly on all operational views.

### 4.2 Hardware Interfaces
HI-1. The system shall interface with smart electricity meters and submeters that expose supported telemetry through standardized or adapter-backed protocols.

HI-2. The system shall interface with IoT sensors for environmental and operational context where required, including temperature, occupancy, or equipment state sensors.

HI-3. The system shall interface with gateways or controllers that bridge field devices to the platform.

HI-4. The system shall interface with load control devices such as relays, smart breakers, or controller endpoints only where explicitly configured and approved.

### 4.3 Software Interfaces
SI-1. The system shall expose secure APIs for telemetry ingestion, dashboard retrieval, reporting, and administration.

SI-2. The system shall support integration with identity providers using standards or agreed customer-specific methods.

SI-3. The system shall support export or integration interfaces for ERP, billing, BMS, SCADA, or data warehouse systems where specified in implementation scope.

SI-4. The system shall provide API authentication and authorization controls consistent with tenant and role boundaries.

### 4.4 Communication Interfaces
CI-1. The system shall support MQTT over TLS for low-overhead telemetry publishing where devices or gateways support it.

CI-2. The system shall support HTTP or HTTPS for polling, push ingestion, and administrative APIs.

CI-3. The system shall support site-to-cloud communication over Ethernet, Wi-Fi, or cellular links.

CI-4. The system shall tolerate delayed or intermittent communication and synchronize data when connectivity is restored.

CI-5. The system shall time-stamp communication failures and restorations for device health analysis.

## 5. Non-Functional Requirements

### 5.1 Performance
NFR-1. The system shall ingest at least 5,000 telemetry messages per minute per deployment instance without message loss under nominal infrastructure sizing.

NFR-2. The system shall make new telemetry available for dashboard display within 10 seconds for at least 95% of messages under nominal load.

NFR-3. The system shall render standard dashboard views within 3 seconds for 95% of requests over a 30-day data range.

NFR-4. The system shall generate standard monthly reports for a single building within 60 seconds for 95% of requests.

### 5.2 Scalability
NFR-5. The system shall support at least 100 buildings and 10,000 devices in a single logical deployment when appropriately provisioned.

NFR-6. The system shall allow horizontal scaling of ingestion and analytics services without requiring changes to device-side integrations.

### 5.3 Security
NFR-7. The system shall encrypt all external network communication using TLS 1.2 or higher.

NFR-8. The system shall store passwords only as salted, one-way cryptographic hashes when local authentication is used.

NFR-9. The system shall enforce least-privilege authorization across tenants, buildings, roles, and control functions.

NFR-10. The system shall automatically terminate inactive authenticated sessions after a configurable timeout not exceeding 30 minutes by default.

NFR-11. The system shall record security-relevant events including failed logins, role changes, API token creation, and control actions.

NFR-12. The system shall support data access and retention controls needed for compliance with applicable Kenyan data protection obligations.

### 5.4 Reliability and Availability
NFR-13. The production platform shall achieve at least 99.5% monthly availability excluding planned maintenance windows.

NFR-14. The system shall queue or buffer inbound telemetry during temporary processing outages and recover without manual data re-entry.

NFR-15. The system shall support automated backups of configuration and historical data.

NFR-16. The system shall target an RPO of 15 minutes and an RTO of 4 hours for production recovery.

### 5.5 Usability
NFR-17. The system shall use consistent units, labels, navigation, and visual states across dashboards and reports.

NFR-18. New facility manager users shall be able to perform the tasks of viewing current usage, acknowledging alerts, and generating a standard report after no more than 4 hours of training.

NFR-19. The interface shall be usable on a 1366x768 desktop display and on modern mobile screens without loss of critical operational information.

### 5.6 Maintainability
NFR-20. The system shall provide structured logs, health endpoints, and diagnostic metrics for operational support.

NFR-21. The system shall separate ingestion, analytics, UI, and integration concerns to allow component-level maintenance and scaling.

NFR-22. Configuration changes for thresholds, schedules, tariffs, and notification routing shall not require code deployment.

### 5.7 Compliance and Auditability
NFR-23. The system shall maintain tamper-evident audit records for administrative and control actions.

NFR-24. The system shall retain audit records for at least 12 months by default, subject to customer policy.

NFR-25. The system shall support evidence generation for energy audits and internal operational reviews.

## 6. Data Requirements

### 6.1 Data Types Collected
DR-1. The system shall support collection of the following telemetry data types where provided by the device: voltage, current, active power, reactive power, apparent power, power factor, frequency, cumulative energy, demand, breaker state, device status, and gateway health.

DR-2. The system should support contextual data such as tariff period, occupancy proxy, ambient temperature, equipment state, and site operating schedule where integration is available.

DR-3. Each telemetry record shall include device identifier, metric name, measured value, timestamp, unit, and data quality indicator.

### 6.2 Data Storage Model
DR-4. The system shall store high-volume telemetry in a time-series data model optimized for timestamped measurements.

DR-5. The system shall store user accounts, configuration, audit logs, rule definitions, and asset metadata in a relational or equivalently structured transactional data model.

DR-6. The system shall maintain logical linkage between telemetry, assets, sites, users, alerts, reports, and control actions.

### 6.3 Data Quality and Integrity
DR-7. The system shall preserve raw ingested values or an auditable equivalent for traceability where feasible.

DR-8. The system shall mark missing, delayed, duplicate, or invalid data conditions distinctly from valid telemetry.

DR-9. The system shall apply clock normalization rules and retain source timestamps where available.

### 6.4 Data Retention and Archival
DR-10. The system shall retain raw telemetry at full resolution for at least 12 months by default, subject to customer contract and storage tier.

DR-11. The system shall support downsampling or aggregation for long-term retention beyond the raw retention period.

DR-12. The system shall retain reports, alerts, and audit logs for at least 12 months by default.

DR-13. The system shall support data export for customer offboarding or migration in a documented machine-readable format.

## 7. System Models

### 7.1 Textual Use Cases
Use Case 1: Monitor Building Consumption  
Primary Actor: Facility Manager  
Preconditions: User is authenticated and assigned to the building. Relevant devices are commissioned.  
Main Flow:

1. User opens the site dashboard.
2. System displays live KPIs, active alerts, and trend charts.
3. User drills down into a feeder or meter showing abnormal load.
4. System displays device-level readings and recent event history.

Postconditions: User identifies current consumption status and any abnormal operating patterns.

Use Case 2: Respond to an Energy Alert  
Primary Actor: Facility Manager or Technician  
Main Flow:

1. System detects a threshold breach or anomaly.
2. System creates an alert and routes notification to authorized users.
3. User reviews alert details and affected asset.
4. User acknowledges the alert.
5. User investigates root cause, records notes, and resolves the issue.
6. System records the full alert lifecycle and timestamps.

Use Case 3: Execute Demand-Limiting Control  
Primary Actor: Authorized Facility Manager  
Preconditions: Control is enabled for the target asset and safety lockout is not active.  
Main Flow:

1. System predicts demand threshold risk or receives a manual control request.
2. System evaluates policy conditions and permissions.
3. User confirms control action if manual approval is required.
4. System issues control command to approved device.
5. Device acknowledges command or returns failure.
6. System logs the result and updates the dashboard.

### 7.2 Data Flow Description
1. Sensors and smart meters measure electrical variables at configured intervals.
2. Devices or gateways publish telemetry to the EMS ingestion interface.
3. The ingestion service validates, deduplicates, time-normalizes, and stores the data.
4. Analytics services compute aggregates, anomalies, forecasts, and recommendations.
5. Alerting services generate events and notifications based on rules or models.
6. UI and reporting services present current state and history to authorized users.
7. Control services send approved commands to eligible downstream devices and record outcomes.

### 7.3 High-Level Architecture Explanation
The system architecture consists of four primary layers:

1. Data Acquisition Layer: smart meters, IoT sensors, controllers, and gateways.
2. Platform Layer: ingestion services, device registry, rules engine, analytics engine, time-series storage, transactional storage, and integration services.
3. Experience Layer: web dashboards, reports, mobile-responsive views, and administration interfaces.
4. Action Layer: notification services, recommendation engine, manual control workflows, and optional automation policies.

This architecture supports the core transformation of data into insight and insight into action while keeping safety controls and auditability explicit.

## 8. Acceptance Criteria

AC-1. The system shall successfully ingest and display live telemetry from at least 20 representative field devices in a test environment with no unhandled ingestion errors during a continuous 24-hour test.

AC-2. At least 95% of valid telemetry points in the acceptance test shall appear in the dashboard within 10 seconds of receipt.

AC-3. The system shall generate alerts for configured threshold breaches and communication failures with correct severity, affected asset, and timestamp in 100% of acceptance test scenarios.

AC-4. Authorized users shall be able to log in, access only permitted buildings and features, and generate standard reports according to their assigned roles in 100% of RBAC test cases.

AC-5. The system shall generate monthly site reports including consumption, peak demand, estimated cost, and alert summary within 60 seconds in the acceptance environment.

AC-6. The system shall preserve audit records for authentication events, configuration changes, and control actions, and those records shall be retrievable through the administrative interface or approved export method.

AC-7. Where automation is in scope, the system shall execute approved control actions only for authorized users and configured assets, and it shall block commands to locked-out or safety-critical assets in 100% of test cases.

AC-8. The system shall recover from a simulated transient network outage by synchronizing buffered telemetry without duplicate final records in the acceptance dataset.

AC-9. The system shall support multi-building views for at least three test sites with site-specific tariffs, thresholds, and user permissions.

AC-10. Stakeholder review shall confirm that the delivered functions support the operational goal of converting raw energy data into actionable insights and controlled cost-saving decisions for building environments.

## Appendix A: Requirement Traceability Guidance

The project team should maintain a traceability matrix mapping each functional and non-functional requirement to:

1. Source stakeholder or business objective.
2. Architecture component.
3. Design artifact.
4. Test case identifier.
5. Deployment or operational control.

## Appendix B: Recommended Future Extensions

The following items are outside the minimum baseline but should be considered in roadmap planning:

1. Integration with utility tariff APIs and outage feeds.
2. Carbon emissions tracking and sustainability dashboards.
3. Occupancy-aware optimization using richer contextual sensors.
4. Machine learning model management and feedback labeling workflows.
5. Native mobile application for technician workflows.