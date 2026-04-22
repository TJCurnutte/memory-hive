# CCaaS Integration Guide: Architecture, Patterns & Vendor Implementations

**Version:** 3.0  
**Author:** CXaaS Specialist  
**Audience:** Contact Center Architects, Integration Engineers, Solution Designers  
**Updated:** April 2026  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [CTI Architecture Deep-Dive](#2-cti-architecture-deep-dive)
3. [CRM Integration: Salesforce](#3-crm-integration-salesforce)
4. [CRM Integration: HubSpot](#4-crm-integration-hubspot)
5. [WFM Integration: NICE, Verint, Aspect](#5-wfm-integration-nice-verint-aspect)
6. [Quality Management Integration](#6-quality-management-qm-integration)
7. [Screen Pop Implementation](#7-screen-pop-implementation)
8. [Contact Flow Design Patterns](#8-contact-flow-design-patterns)
9. [Real-Time Data Exchange](#9-real-time-data-exchange)
10. [Integration Testing Strategy](#10-integration-testing-strategy)
11. [Appendix: API Quick Reference](#appendix-api-quick-reference)

---

## 1. Introduction

### 1.1 What This Guide Covers

This document provides a comprehensive, vendor-neutral reference for integrating Contact Center-as-a-Service (CCaaS) platforms with the ecosystems that surround them: CRMs, Workforce Management (WFM) systems, Quality Management (QM), Computer Telephony Integration (CTI), and real-time data pipelines. It is built from current industry standards, published API architectures, and integration patterns in active production use.

### 1.2 What CCaaS Integration Means

A modern CCaaS platform is rarely a standalone system. It exists within an ecosystem:

```
                    ┌──────────────────────────┐
                    │   CCaaS Platform         │
                    │   (Genesys/Twilio/etc.)  │
                    └──────────┬───────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼──────┐      ┌──────▼──────┐     ┌──────▼──────┐
    │    CRM     │      │    WFM      │     │     QM      │
    │Salesforce  │      │ NICE/Verint │     │  eGain      │
    │ HubSpot    │      │  Aspect     │     │ NICE WFM QM │
    └────────────┘      └─────────────┘     └─────────────┘
          │                    │                    │
    ┌─────▼──────┐      ┌──────▼──────┐     ┌──────▼──────┐
    │   HRIS     │      │   Analytics │     │   SIP/ PSTN │
    │  Payroll   │      │   Tableau   │     │  Trunking   │
    └────────────┘      └─────────────┘     └─────────────┘
```

The integration layer connects these systems to orchestrate a seamless agent and customer experience.

### 1.3 Key Integration Principles

- **Event-driven over polling** — Use webhooks and streaming APIs instead of scheduled polling where real-time response is required.
- **Idempotency** — All write operations (log activities, create cases) should be idempotent to handle retries gracefully.
- **Authentication standardisation** — Use OAuth 2.0 / JWT everywhere. Avoid storing credentials in config files.
- **Semantic versioning** — When building webhook payloads, version them and maintain a changelog.
- **Observability** — Every integration point should have logging, alerting, and tracing.

---

## 2. CTI Architecture Deep-Dive

### 2.1 What is CTI?

Computer Telephony Integration (CTI) is the layer that connects the telephone network to software systems. In a CCaaS context, CTI is what enables:

- Screen pops (opening a CRM record when a call arrives)
- Click-to-dial (initiating a call from within an application)
- Call control (hold, transfer, conference) from the CRM interface
- Call logging and activity recording back to the CRM
- Real-time call state monitoring

### 2.2 Genesys Cloud CTI Architecture

Genesys Cloud is a cloud-native CCaaS platform with robust CTI capabilities via its Platform API (REST + WebSocket).

```
Genesys Cloud CTI Stack
├── PureCloud Telephony (SIP-based)
├── WebSocket Event Stream (real-time call events)
├── Architect (flow designer, cloud-native IVR/ACD)
├── Data Actions (external integrations via HTTP)
├── Platform API (REST — /api/v2)
└── SCIM / OAuth 2.0 Authentication
```

#### Key API Endpoints (Genesys Cloud)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v2/conversations/calls/actions/transfer` | Transfer a call |
| `POST /api/v2/users/{userId}/calls` | Initiate an outbound call (click-to-dial) |
| `GET /api/v2/conversations/{conversationId}` | Get call details |
| `POST /api/v2/data-actions` | Invoke external integration (e.g., CRM lookup) |
| `GET /api/v2/queues/{queueId}/members` | Get queue membership for routing |

#### Genesys WebSocket for Real-Time Events

Genesys Cloud uses a WebSocket-based event stream for real-time call and agent state:

```javascript
// Connecting to Genesys Cloud event stream
const wssUrl = `wss://streaming.{cluster}.genesys.cloud`;
const token = 'YOUR_OAUTH_TOKEN';

// Subscribe to conversation events
const message = {
  "topicName": "Conversations",
  "version": "1.0",
  "action": "start"
};
```

Event types include: `v2.conversations.{id}.calls.started`, `v2.conversations.{id}.calls.ended`, `v2.users.{id}.routing-status`.

#### Genesys Data Actions (Outbound Webhooks)

Data Actions in Genesys Architect are outbound HTTP calls used to:

- Look up customer in Salesforce by ANI (phone number)
- Retrieve open cases from HubSpot
- Create a ticket in Zendesk
- Fetch agent schedule from WFM system

Configuration requires: URL, HTTP method, headers (including auth), request template, response mapping.

### 2.3 Twilio Flex CTI Architecture

Twilio Flex is a programmable contact center platform built on Twilio's core voice, SMS, and chat APIs.

```
Twilio Flex CTI Stack
├── TaskRouter (routing engine)
├── Studio (visual flow builder)
├── Functions (serverless compute)
├── Sync (real-time state)
├── Flex UI (React-based agent interface)
├── Plugins (custom UI components)
└── REST API (Twilio account-level)
```

#### Twilio TaskRouter API

TaskRouter handles work distribution. Key concepts: Worker, Task, Activity, Workspace.

```javascript
// Retrieve a task by SID
const task = await client.taskrouter.v1
  .workspaces(process.env.WORKSPACE_SID)
  .tasks(taskSid)
  .fetch();

// Update task attributes (e.g., set customer data for screen pop)
await client.taskrouter.v1
  .workspaces(process.env.WORKSPACE_SID)
  .tasks(taskSid)
  .update({ attributes: JSON.stringify(enrichedAttributes) });
```

#### Twilio Flex Plugins — Screen Pop Pattern

A Flex plugin can subscribe to TaskAssigned events and use the task attributes to open the CRM record:

```javascript
// flex-plugin-crm-pop/src/CrmPop.js
import React, { useEffect } from 'react';
import { TaskHelper, Template, TemplateSource } from '@twilio/flex-ui';

export function CrmPopManager(flex: Flex, manager: Manager) {
  // Listen for task assignment
  flex.Events.addListener('taskAssigned', async (task) => {
    const attributes = task.attributes || {};
    const phone = attributes.from || attributes.customerPhone;
    
    // Screen pop to Salesforce
    if (attributes.crmType === 'salesforce') {
      const searchUrl = `${SALESFORCE_INSTANCE_URL}/search?q=${encodeURIComponent(phone)}`;
      // Open in new tab or side panel
      window.open(searchUrl, '_blank');
    }
  });
}
```

#### Twilio Studio for Contact Flow Design

Studio allows visual flow design with HTTP Request widgets for CRM integration:

1. **Incoming call** → Trigger Studio Flow
2. **Enqueue** → Assign to TaskRouter queue
3. **HTTP Request Widget** → Lookup CRM contact by ANI
4. **Split based on** → Contact found / not found
5. **If found** → Set task attributes with contact data for screen pop
6. **If not found** → Collect account number → Create lead in CRM

#### Twilio Sync for Real-Time State

Twilio Sync allows real-time data sharing across channels and components. Used for:

- Synchronising queue wait times across agent desktops
- Sharing context between IVR and agent desktop
- Real-time co-browsing session data

```javascript
// Twilio Sync: update a document with call context
const syncService = client.sync.v1.services(process.env.SYNC_SERVICE_SID);
await syncService.documents('call-context').update({
  data: {
    callSid: call.Sid,
    customerName: lookupResult.name,
    accountTier: lookupResult.tier,
    lastContact: lookupResult.lastContactDate
  }
});
```

### 2.4 Generic CTI Integration Patterns

Regardless of vendor, CTI integrations follow a common architectural pattern:

```text
Phone Network (PSTN/SIP)
        │
        ▼
  Telephony Platform (Genesys/Twilio/NICE)
        │
        ▼ (Event Webhooks / WebSocket)
  CTI Middleware Layer (optional — e.g., Voxeo, Solstice)
        │
        ▼ (REST API / SDK)
  CRM / WFM / QM Systems
        │
        ▼
  Agent Desktop (screen pop, controls)
```

### 2.5 Click-to-Dial Implementation

Click-to-dial from a CRM involves:

1. **Agent clicks phone number** in CRM UI
2. **CRM sends API call** to CCaaS platform to initiate outbound call
3. **CCaaS platform calls the agent** (front-channel)
4. **CCaaS platform calls the customer** (back-channel)
5. **Agent and customer are connected** (bridged call)
6. **CRM receives call initiation event** and opens contact record
7. **Call is logged back to CRM** on termination

#### Salesforce + Genesys (Click-to-Dial Example)

```apex
// Salesforce Apex Controller for Click-to-Dial
public class CTIClickToDialController {
    
    @AuraEnabled
    public static String initiateCall(String phoneNumber, String contactId) {
        // Call Genesys Cloud API
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:GenesysCloud/users/' + agentUserId + '/calls');
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + getGenesysToken());
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(new Map<String, String>{
            'dialPlan' => phoneNumber,
            'callFromId' => genesysQueueId
        }));
        
        Http http = new Http();
        HttpResponse res = http.send(req);
        return res.getBody();
    }
}
```

#### HubSpot + Twilio (Click-to-Dial Example)

```javascript
// HubSpot custom card + Twilio Flex integration
async function initiateClickToDial(phoneNumber, contactId) {
  // Use HubSpot CRM API to get agent's Twilio-compatible phone
  const contact = await hubspotClient.crm.contacts.basicApi.getById(contactId);
  
  // Initiate call via Twilio TaskRouter
  const task = await twilioClient.taskrouter.v1
    .workspaces(process.env.TWILIO_WORKSPACE_SID)
    .tasks.create({
      attributes: JSON.stringify({
        type: 'click_to_dial',
        customerPhone: phoneNumber,
        customerName: contact.properties.firstname + ' ' + contact.properties.lastname,
        agentContactId: contactId
      }),
      workflowSid: process.env.CTD_WORKFLOW_SID,
      taskChannel: 'TC_OutboundCall'
    });
  
  return task.sid;
}
```

---

## 3. CRM Integration: Salesforce

### 3.1 Salesforce Connected App Setup

Before any integration, configure a Salesforce Connected App:

1. **Setup → App Manager → New Connected App**
2. Enable OAuth settings, add scopes: `api`, `refresh_token`, `full`
3. Set callback URL (e.g., `https://your-ccaaS-domain/auth/callback`)
4. Save Consumer Key and Consumer Secret
5. Assign to appropriate profiles/IP ranges
6. Configure Named Credentials in Salesforce for secure auth

### 3.2 Screen Pop Implementation (Salesforce)

Screen pop is triggered when an inbound call's ANI (Automatic Number Identification) matches an existing Contact or Lead in Salesforce.

#### Flow: ANI → Salesforce Search → Screen Pop

```text
Inbound Call ANI
       │
       ▼
CCaaS Platform extracts ANI
       │
       ▼
HTTP POST to Salesforce REST API: 
  GET /services/data/v59.0/search?q=SELECT+Id+FROM+Contact+WHERE+Phone='{ANI}'
       │
       ▼
Contact Found?
  │         │
 Yes       No
  │         │
  ▼         ▼
Open URL:  Create New Contact
/sfdc/Customer/Case/{Id}  form pre-filled with ANI
       │
       ▼
Agent sees screen pop with customer context
```

#### Salesforce Web-to-Lead as Fallback

For unknown callers without a matched contact:

```javascript
// Salesforce Web-to-Lead / API Lead creation
async function createLeadFromUnknownCaller(ani, flowData) {
  const leadPayload = {
    LastName: 'Unknown Caller',
    Phone: ani,
    Company: 'Unknown',
    Description: `Inbound call from ${ani} - no contact match found`,
    LeadSource: 'Inbound Call',
    Status: 'New'
  };
  
  const response = await sfApiClient.sobjects.Lead.create(leadPayload);
  return response;
}
```

### 3.3 Logging Activities to Salesforce

After every call, the CCaaS platform should log a Task or Call Log to Salesforce. This is critical for reporting and agent performance visibility.

#### Log a Call Task via REST API

```javascript
async function logCallActivity(callData, salesforceContactId) {
  const taskPayload = {
    Subject: `Inbound Call - ${callData.disposition}`,
    Status: 'Completed',
    Priority: 'Normal',
    WhoId: salesforceContactId,       // Contact or Lead ID
    WhatId: callData.caseId || null,  // Optional: related Case
    CallType: callData.direction,      // 'Inbound' | 'Outbound'
    CallDuration: Math.round(callData.durationSeconds),
    CallObject: callData.callSid,
    Description: `Call duration: ${formatDuration(callData.durationSeconds)}. 
                  Queue: ${callData.queueName}. 
                  Agent: ${callData.agentName}.`,
    ActivityDate: new Date().toISOString().split('T')[0]
  };
  
  const result = await sfClient.sobjects.Task.create(taskPayload);
  return result.id;
}
```

#### Salesforce Open CTI (Agent Console Integration)

For deeper CTI integration in Salesforce Lightning, use the Open CTI API:

```javascript
// Salesforce Open CTI — softphone layout integration
import { LightningElement, wire } from '@lwc/core';
import { getCallObject } from 'lightning/platformOpenCTI';

// Listen for call events from CCaaS platform
@wire(getCallObject, { apiName: 'CALL_OBJECT' })
callObject;

handleCallStart(event) {
  // event.detail contains call SID, ANI, direction
  const { ani, callId } = event.detail;
  
  // Search Salesforce for matching contact
  searchContactsByPhone(ani).then(contact => {
    // Open screen pop
    searchContactsByPhone(ani).then(contact => {
      // Navigate to contact record
      this[NavigationMixin.Navigate]({
        type: 'standard__recordPage',
        attributes: { recordId: contact.id, actionName: 'view' }
      });
    });
  });
}
```

### 3.4 Case Creation from Contact Center

For support-oriented contact centers, creating a Salesforce Case at call wrap-up is a common pattern:

```javascript
async function createCaseFromCall(callData, contactId) {
  const casePayload = {
    Subject: callData.subject || `Call - ${callData.customerPhone}`,
    Description: callData.notes || 'See activity log for details.',
    Status: 'New',
    Priority: mapPriority(callData.urgency),
    Origin: 'Phone',
    ContactId: contactId,
    OwnerId: getNextTierQueueId(callData.category), // Escalation routing
    // Custom fields commonly used:
    Internal_Category__c: callData.category,
    First_Contact_Resolution__c: callData.resolvedOnFirstCall,
    CSAT_Score__c: null // Populated post-survey
  };
  
  const sfCase = await sfClient.sobjects.Case.create(casePayload);
  return sfCase.id;
}
```

### 3.5 Salesforce CTI Adapter Configuration

The Salesforce CTI Adapter (available in Setup → CTI Adapter) allows:

- Configure softphone layout (which CRM fields to show on screen pop)
- Set call centre hours
- Map disposition codes to Salesforce statuses
- Define screen pop rules (on call arrival, on call disconnect, on wrap-up)

**Screen pop rule example:**

| Rule Type | Condition | Action |
|-----------|-----------|--------|
| On Call Arrival | ANI matches Contact.Phone | Pop Contact page |
| On Call Arrival | ANI matches Lead.Phone | Pop Lead page |
| On Call Arrival | No match | Pop new Case form with ANI |
| On Wrap-Up | Disposition = Complaint | Route to Queue B |

---

## 4. CRM Integration: HubSpot

### 4.1 HubSpot Private App Setup

HubSpot integrations use Private Apps rather than OAuth for server-side access:

1. **Settings → Integrations → Private Apps → Create a private app**
2. Scopes needed: `crm.objects.contacts.read`, `crm.objects.deals.read`, `crm.objects.tasks.write`, `crm.objects.owners.read`
3. Store the access token securely (environment variable, secret manager)

### 4.2 Contact Sync & De-duplication

HubSpot contact matching is typically done on email or phone number. Use the Contacts API to search:

```javascript
async function findHubSpotContactByPhone(phone) {
  // Normalize phone number
  const normalizedPhone = normalizePhoneNumber(phone);
  
  const searchResponse = await hubspotClient.apiRequest({
    method: 'POST',
    path: '/crm/v3/objects/contacts/search',
    body: {
      filterGroups: [{
        filters: [{
          propertyName: 'phone',
          operator: 'EQ',
          value: normalizedPhone
        }]
      }],
      properties: ['firstname', 'lastname', 'email', 'phone', 'lifecyclestage', 'hs_lead_status']
    }
  });
  
  const results = JSON.parse(searchResponse).results;
  return results.length > 0 ? results[0] : null;
}
```

**De-duplication strategy:**

| Priority | Match Field | Fallback |
|----------|------------|----------|
| 1 | Email (exact) | Use existing contact |
| 2 | Phone (E.164 normalized) | Match or create |
| 3 | Name + Company | Merge if high confidence |
| 4 | No match | Create new contact |

### 4.3 Deal Stage Triggers

HubSpot Deals change stage when certain events occur in the contact center. For example, a "High Priority" call about a billing issue might advance a deal stage.

```javascript
async function handleDealStageChangeBasedOnCall(callData) {
  const dealId = callData.associatedDealId;
  
  if (!dealId) return;
  
  // Determine new stage based on call outcome
  let newStage;
  if (callData.disposition === 'complaint_resolved') {
    newStage = 'appointmentscheduled'; // HubSpot deal stage
  } else if (callData.disposition === 'upgrade_interest') {
    newStage = 'qualifiedtobuy';
  } else if (callData.disposition === 'churn_risk') {
    newStage = 'presentationscheduled'; // flag for retention team
  }
  
  if (newStage) {
    await hubspotClient.crm.deals.basicApi.update(dealId, {
      properties: {
        dealstage: newStage,
        closedate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        // Append call notes to deal description
        notes_last_updated: `Call on ${new Date().toISOString()}: ${callData.summary}`
      }
    });
  }
}
```

### 4.4 HubSpot Task Creation from Contact Center

When a call requires follow-up (callback request, complaint, incomplete resolution), create a HubSpot Task:

```javascript
async function createHubSpotTask(taskData) {
  const taskPayload = {
    hs_task_subject: taskData.subject,
    hs_task_body: taskData.notes || '',
    hs_task_status: 'NOT_STARTED',
    hs_task_priority: taskData.priority === 'urgent' ? 'HIGH' : 'MEDIUM',
    // Link to associated contact
    hubspot_owner_id: taskData.assigneeOwnerId,
    // Due date: set to next business day for follow-ups
    hs_timestamp: calculateNextBusinessDay(taskData.dueInHours).getTime()
  };
  
  // Associate task with contact
  const associations = [{
    to: { id: taskData.contactId },
    types: [{
      associationCategory: 'HUBSPOT_DEFINED',
      associationTypeId: 3 // Contact → Task
    }]
  }];
  
  const task = await hubspotClient.crm.tasks.basicApi.create(
    taskPayload,
    associations
  );
  
  return task.id;
}
```

### 4.5 HubSpot Workflow Enrollment

HubSpot Workflows can be triggered via Webhook when CCaaS events occur:

```javascript
async function enrollInHubSpotWorkflow(contactId, workflowEvent) {
  // HubSpot Workflows API (v3)
  await hubspotClient.apiRequest({
    method: 'POST',
    path: `/automation/v3/workflows/${WORKFLOW_ID}/enrollments`,
    body: {
      email: workflowEvent.contactEmail,
      properties: {
        last_call_date: workflowEvent.callDate,
        call_disposition: workflowEvent.disposition,
        call_recording_url: workflowEvent.recordingUrl,
        agent_id: workflowEvent.agentId
      }
    }
  });
}

// Map CCaaS events to HubSpot workflow enrollments
const workflowMap = {
  'call_completed_no_resolution': UPSELL_WORKFLOW_ID,
  'callback_requested': FOLLOWUP_WORKFLOW_ID,
  'complaint_flagged': ESCALATION_WORKFLOW_ID,
  'vip_customer': VIP_TREATMENT_WORKFLOW_ID
};
```

---

## 5. WFM Integration: NICE, Verint, Aspect

### 5.1 Workforce Management Integration Overview

WFM systems are responsible for:

- **Forecasting** — Predicting contact volume based on historical data
- **Scheduling** — Building agent schedules to meet forecast
- **Real-time adherence** — Monitoring whether agents are on-schedule
- **Intraday management** — Adjusting schedules as actual volume deviates from forecast

The CCaaS platform must share data with the WFM system bidirectionally:

```
CCaaS Platform               WFM System
─────────────                ──────────
Real-time volumes ──────────► Forecast vs. Actual tracking
Agent schedule ◄──────────── Agent schedule data (via ADK/ICS)
Adherence events ──────────► Adherence scoring
Historical stats ──────────► Reports & forecasting model updates
```

### 5.2 NICE WFM Integration

NICE (formerly NICE Ltd.) offers several products in the contact center space: NICE Workforce Management (WFM), NICE Enlighten (AI), and NICE Quality Management (QM).

#### NICE WFM Agent Database (ADK) Integration

NICE WFM uses an Agent Database (ADK) that can be synchronised via flat files or real-time API:

| Data Element | Direction | Frequency |
|-------------|-----------|-----------|
| Agent IDs and names | WFM → CCaaS | Daily / on-change |
| Agent skills | WFM → CCaaS | Daily |
| Agent schedule | WFM → CCaaS | Daily (and real-time intraday updates) |
| Actual adherence data | CCaaS → WFM | Real-time (per event) |
| Staffed/unstaffed state | CCaaS → WFM | Real-time |
| Queue occupancy | CCaaS → WFM | Every N seconds (configurable, e.g., 30s) |

#### NICE IEX (Interaction Exchange) Web Services

NICE IEX is a data exchange layer. Typical integration:

```xml
<!-- NICE IEX SOAP request for intraday data submission -->
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Header>
      <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/...">
         <wsse:UsernameToken>
            <wsse:Username>CCaaS_INTEGRATION_USER</wsse:Username>
            <wsse:Password Type="...">...</wsse:Password>
         </wsse:UsernameToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <SubmitIntervalData>
         <intervalStart>{ISO8601_TIMESTAMP}</intervalStart>
         <intervalDuration>900</intervalDuration>
         <metrics>
            <queueId>SUPPORT_QUEUE_1</queueId>
            <offered>47</offered>
            <handled>42</handled>
            <avgWaitTime>45</avgWaitTime>
            <serviceLevel>0.87</serviceLevel>
         </metrics>
      </SubmitIntervalData>
   </soapenv:Body>
</soapenv:Envelope>
```

#### NICE Real-Time Adherence API (RTA)

NICE WFM tracks Real-Time Adherence (RTA) by comparing what the agent is doing versus their schedule. The CCaaS platform publishes agent state changes:

```javascript
// NICE WFM RTA: publish agent state change
async function publishAdherenceEvent(agentEvent) {
  const adherencePayload = {
    agentId: agentEvent.agentId,
    activityCode: mapToWFMCode(agentEvent.activityCode),
    startTime: agentEvent.timestamp,
    source: 'CCaaS',
    mediaType: agentEvent.channel // 'VOICE' | 'CHAT' | 'EMAIL'
  };
  
  // Use NICE WFM REST API or IPC file drop
  await niceWFMClient.submitAdherence(adherencePayload);
}

// Map CCaaS activity codes to NICE activity codes
const activityMap = {
  'AVAILABLE': 'Available',
  'ON_CALL': 'On Contact',
  'AFTER_CALL_WORK': 'ACW',
  'BREAK': 'Break',
  'MEETING': 'Meeting',
  'TRAINING': 'Training',
  'OFFLINE': 'Unscheduled'
};
```

### 5.3 Verint WFM Integration

Verint (now part of Verint-Customer Engagement Cloud) offers Workforce Optimization including WFM, QM, and Analytics.

#### Verint Interaction API (IPC)

Verint uses an Interaction Processing Client (IPC) for real-time data exchange:

```javascript
// Verint WFM: publish contact statistics
async function submitVerintContactStats(statsData) {
  const verintRecord = {
    mediaType: 'VOICE',
    queueId: statsData.queueName,
    intervalStart: statsData.intervalStart,
    intervalEnd: statsData.intervalEnd,
    offered: statsData.offered,
    answered: statsData.answered,
    abandoned: statsData.abandoned,
    avgWaitTimeSeconds: statsData.averageWaitTime,
    maxWaitTimeSeconds: statsData.maxWaitTime,
    serviceLevelPercentage: calculateSL(statsData.answered, statsData.offered, statsData.slThresholdSeconds)
  };
  
  // Via IPC file drop or REST API
  await verintWFMClient.submitIntervalData(verintRecord);
}
```

#### Verint Scheduling Data Feed

Verint receives schedule data from the CCaaS platform or exports schedules via:

1. **File-based (ICS/CSV)** — Standard for multi-vendor environments
2. **Real-time API** — For intraday updates
3. **SCIM** — For user/provisioning sync

**ICS (iCalendar) schedule export** is the most vendor-neutral approach:

```javascript
// Generate ICS schedule file for Verint WFM import
function generateICSSchedule(agentSchedule) {
  const events = agentSchedule.map(s => ({
    uid: `${s.agentId}-${s.startTime.getTime()}@yourcompany.com`,
    summary: `Shift - ${s.activity}`,
    dtstart: formatICSDate(s.startTime),
    dtend: formatICSDate(s.endTime),
    description: `Agent: ${s.agentName}, Queue: ${s.queue}`,
    categories: s.activity
  }));
  
  return generateICSFile(events); // ics npm package
}

// Upload to Verint SFTP dropbox
await uploadToSFTP(icsFile, '/wfm/inbound/schedule_import');
```

### 5.4 Aspect WFM Integration

Aspect provides workforce optimization including Aspect WFM (formerly Aspect Workforce Management).

#### Aspect RPM (Real-Time Metrics) Interface

Aspect WFM collects real-time metrics via its RPM (Real-time Performance Management) interface:

```javascript
// Aspect WFM RPM: periodic data submission
async function submitAspectRPMData(metrics) {
  const rpmRecord = {
    siteId: process.env.ASPECT_SITE_ID,
    interval: Math.floor(Date.now() / 900000) * 900, // 15-min interval boundary
    queueMetrics: metrics.map(m => ({
      skillGroupId: m.skillGroupId,
      offered: m.offered,
      handled: m.handled,
      avgWaitTime: m.averageWaitSeconds,
      serviceLevel: m.serviceLevel / 100,
      occupancy: m.agentOccupancy / 100
    }))
  };
  
  // Publish to Aspect RPM via HTTPS endpoint
  await axios.post(
    `${ASPECT_RPM_URL}/api/v1/metrics`,
    rpmRecord,
    { headers: { 'X-API-Key': process.env.ASPECT_API_KEY } }
  );
}
```

#### Aspect Schedule Publishing

Aspect WFM exports agent schedules that the CCaaS platform imports to configure agent availability and routing profiles:

```json
// Example: Agent schedule data from Aspect WFM (JSON export)
{
  "agentId": "AGT-1001",
  "siteId": "SITE-001",
  "schedule": [
    {
      "start": "2026-04-22T08:00:00Z",
      "end": "2026-04-22T16:00:00Z",
      "activity": "Scheduled",
      "skillGroup": "SALES_QUEUE"
    },
    {
      "start": "2026-04-22T12:00:00Z",
      "end": "2026-04-22T12:30:00Z",
      "activity": "Break",
      "skillGroup": null
    }
  ]
}
```

### 5.5 WFM Integration Data Model

Regardless of vendor, a standard data model underlies all WFM integrations:

| Data Item | CCaaS Role | WFM Role | Frequency |
|-----------|-----------|----------|-----------|
| Agent list | Publish | Consume | Daily / on-change |
| Agent skills | Publish | Consume | Daily |
| Agent schedule | Consume | Publish | Daily + intraday |
| Real-time occupancy | Publish | Consume | Every 30s |
| Intraday volume updates | Publish | Consume | Every 15 min |
| Adherence events | Publish | Consume | Real-time |
| Historical performance | Publish | Consume | Daily rollup |
| Forecast data | Consume | Publish | Daily (next-day) |

---

## 6. Quality Management (QM) Integration

### 6.1 QM Integration Overview

Quality Management systems record interactions (calls, chats, emails), enable supervisors to evaluate them against scorecards, and generate coaching insights.

### 6.2 Recording Integration

CCaaS platforms must deliver call recordings to the QM system. Two primary patterns:

#### Pattern A: Push via Webhook/Callback

The CCaaS platform pushes recording metadata (and optionally the recording file) to the QM system when a call completes.

```javascript
// On call completion: notify QM system
async function notifyQMOfCompletedCall(callRecord) {
  const qmPayload = {
    callSid: callRecord.callSid,
    agentId: callRecord.agentId,
    customerPhone: callRecord.customerPhone,
    queueName: callRecord.queueName,
    startTime: callRecord.startTime,
    endTime: callRecord.endTime,
    duration: callRecord.durationSeconds,
    disposition: callRecord.disposition,
    recordingUrl: callRecord.recordingUrl,
    screenRecordingUrl: callRecord.screenRecordingUrl,
    // Additional metadata for evaluation criteria
    wasTransferred: callRecord.transferred,
    wasEscalated: callRecord.escalated,
    customerSentiment: callRecord.avgSentimentScore,
    sentimentAlerts: callRecord.sentimentAlerts // e.g., raised voice detected
  };
  
  await qmClient.apiRequest({
    method: 'POST',
    path: '/api/v1/interactions',
    body: qmPayload
  });
}
```

#### Pattern B: Recording Delivered via Media Storage (S3/GCS)

1. CCaaS platform uploads recording to an S3 bucket (or GCS)
2. QM system polls the bucket or receives an S3 event notification
3. QM system ingests the recording along with associated metadata

This pattern is preferred for large volumes as it offloads media transfer to object storage.

```javascript
// Configure S3 event notification for QM system
const s3RecordingConfig = {
  bucket: 'ccaa-recordings-prod',
  prefix: 'calls/',
  eventTypes: ['s3:ObjectCreated:Put'],
  // Trigger QM ingestion Lambda
  notificationLambda: 'qm-recording-ingestion-lambda'
};

// Lambda: on recording upload, notify QM system
async function handleRecordingUpload(record) {
  const recordingMeta = {
    s3Key: record.s3.key,
    s3Bucket: record.s3.bucket.name,
    callSid: extractCallSidFromKey(record.s3.key),
    uploadTimestamp: new Date().toISOString()
  };
  
  await qmSystem.ingestRecording(recordingMeta);
}
```

### 6.3 Evaluation & Coaching Workflow

Once recordings are in the QM system, the evaluation workflow is:

```
Recording Available
       │
       ▼
QM System assigns to supervisor queue (or auto-distributes by rule)
       │
       ▼
Supervisor selects interaction for evaluation
       │
       ▼
QM Scorecard completed (e.g., product knowledge, empathy, compliance)
       │
       ▼
Coaching plan generated / pushed to agent's learning system
       │
       ▼
Agent notified of coaching session (via email, LMS, or in-app)
       │
       ▼
QM analytics surface patterns (top performers, common gaps)
```

### 6.4 NICE QM (NiceConnect) Integration

NICE QM (formerly NICE Quality Management / NICE IEX WFM Quality) integrates via:

```javascript
// NICE QM: Submit evaluation results back to CCaaS for reporting
async function syncEvaluationToCCaaS(evaluationResult) {
  // After supervisor completes evaluation
  const coachingData = {
    agentId: evaluationResult.agentId,
    evaluationDate: evaluationResult.date,
    score: evaluationResult.totalScore,
    scoreBreakdown: evaluationResult.criteriaScores,
    strengths: evaluationResult.strengths,
    improvementAreas: evaluationResult.areasForDevelopment,
    coachingRecommended: evaluationResult.recommendedForCoaching,
    evaluatorId: evaluationResult.supervisorId
  };
  
  // Push to CCaaS platform for agent performance tracking
  await ccassPlatform.updateAgentScore(evaluationData);
}
```

### 6.5 Real-Time Quality Alerts (Speech Analytics)

Modern QM systems use speech analytics to surface quality issues in real time:

| Trigger | Action |
|---------|--------|
| Customer says "supervisor" / "manager" | Alert supervisor, flag for review |
| Negative sentiment spike | Trigger supervisor whisper or alert |
| Compliance keyword missed | Flag for QA review + compliance alert |
| Long silence detected | Check if customer needs assistance |
| Agent overtalk percentage too high | Coaching flag |

```javascript
// Real-time speech analytics alert integration
async function handleSpeechAnalyticsAlert(alertData) {
  if (alertData.severity === 'critical') {
    // Page supervisor for immediate intervention
    await supervisorClient.sendAlert({
      agentId: alertData.agentId,
      type: 'SPEECH_ALERT',
      message: `Critical: Customer said "${alertData.triggerPhrase}"`,
      url: alertData.callRecordingUrl
    });
    
    // Notify contact center dashboard
    await dashboardClient.updateCallFlags({
      callSid: alertData.callSid,
      flags: ['SPEECH_ALERT', 'SUPERVISOR_ALERTED']
    });
  }
  
  // Store for post-contact evaluation
  await evaluationQueue.add({
    callSid: alertData.callSid,
    alertType: alertData.type,
    alertSeverity: alertData.severity,
    timestamp: alertData.timestamp
  });
}
```

---

## 7. Screen Pop Implementation

### 7.1 Screen Pop Architecture

Screen pop is the display of relevant customer information when a call is presented to an agent. The goal is to give the agent context before they answer, reducing Average Handle Time (AHT) and improving First Call Resolution (FCR).

```
Call Arrives at Agent Desktop
        │
        ▼
CCaaS extracts ANI / DNIS from call setup (SIP INVITE / PSTN IAM)
        │
        ▼
Lookup Request to CRM (or CTI middleware)
        │
        ▼
CRM search by phone / customer ID
        │
        ▼
CRM returns customer record (or "not found")
        │
        ▼
CCaaS opens CRM URL in agent desktop (iframe / new tab / side panel)
        │
        ▼
Agent sees customer history before answering
```

### 7.2 Screen Pop Data Flow (Genesys Cloud)

```javascript
// Genesys Cloud: Architect flow with data action for screen pop
const screenPopFlow = {
  name: 'Inbound_Screen_Pop_Flow',
  trigger: 'INBOUND_CALL',
  steps: [
    {
      id: 'lookup_ani',
      type: 'DATA_ACTION',
      action: {
        name: 'CRM_Lookup',
        uri: 'https://api.yourcrm.com/lookup',
        requestTemplate: {
          method: 'GET',
          headers: { 'Authorization': 'Bearer {credentials.CRM_TOKEN}' },
          queryParams: { 'phone': '{call.ani}' }
        },
        responseMapping: {
          contactFound: '{ContactExists}',
          contactId: '{Contact.Id}',
          contactName: '{Contact.Name}',
          accountTier: '{Contact.Account.Tier}'
        }
      }
    },
    {
      id: 'branch_on_contact',
      type: 'SPLIT',
      branches: [
        { condition: 'lookup_ani.contactFound == true', nextStep: 'open_sfdc' },
        { condition: 'lookup_ani.contactFound == false', nextStep: 'open_new_contact_form' }
      ]
    },
    {
      id: 'open_sfdc',
      type: 'DATA_ACTION',
      action: {
        name: 'OpenScreenPop',
        type: 'OPEN_URL',
        uri: 'https://yourorg.my.salesforce.com/{lookup_ani.contactId}'
      }
    }
  ]
};
```

### 7.3 Screen Pop Data (Twilio Flex)

In Twilio Flex, screen pop data is passed via Task attributes:

```javascript
// Twilio Studio: Set task attributes for screen pop
const screenPopAttributes = {
  // Customer identification
  customerName: lookupResult.fullName,
  customerPhone: call.ani,
  customerEmail: lookupResult.email,
  customerAccountId: lookupResult.accountId,
  
  // Context for agent
  accountTier: lookupResult.accountTier,
  openCases: lookupResult.openCaseCount,
  lastContactDate: lookupResult.lastContactDate,
  lastContactOutcome: lookupResult.lastDisposition,
  recentPurchases: lookupResult.recentOrderIds,
  
  // Routing hints
  language: lookupResult.preferredLanguage,
  preferredAgentTeam: lookupResult.segmentTeam,
  
  // CRM metadata
  crmType: 'salesforce',
  crmUrl: `https://yourorg.salesforce.com/${lookupResult.contactId}`,
  crmObjectType: 'Contact'
};

// Pass to task router
const task = await twilioClient.taskrouter.v1
  .workspaces(WORKSPACE_SID)
  .tasks.create({
    attributes: JSON.stringify(screenPopAttributes),
    workflowSid: WORKFLOW_SID,
    taskChannel: 'VOICE'
  });
```

### 7.4 Screen Pop URL Generation Patterns

| CRM | Screen Pop URL Pattern |
|-----|------------------------|
| Salesforce Classic | `https://{instance}.salesforce.com/{contactId}` |
| Salesforce Lightning | `https://{instance}.lightning.force.com/lightning/r/Contact/{contactId}/view` |
| HubSpot | `https://app.hubspot.com/contacts/{contactId}` |
| Zendesk | `https://{subdomain}.zendesk.com/agent/tickets/{ticketId}` |
| Microsoft Dynamics | `https://{org}.crm.dynamics.com/main.aspx?etn=contact&id={contactId}` |
| Custom App | `https://your-app.com/customer/{contactId}?source=screenpop` |

### 7.5 Screen Pop Configuration Checklist

- [ ] ANI (caller phone number) is captured from SIP/PSTN signaling
- [ ] Phone number is normalised to E.164 format before CRM lookup
- [ ] CRM lookup timeout is set (recommend: 2-3 seconds max)
- [ ] Fallback behavior is defined for: CRM unavailable, contact not found, timeout
- [ ] Screen pop URL opens in appropriate context (iframe, side panel, or new tab)
- [ ] Agent sees customer data BEFORE answering the call
- [ ] Data is passed via secure, authenticated channels
- [ ] Logging captures: screen pop success/failure, lookup duration, CRM response

---

## 8. Contact Flow Design Patterns

### 8.1 Contact Flow Fundamentals

Contact flows (also called IVR flows, call flows, or routing strategies) are the logical paths a customer takes through the contact center. Good flow design balances customer effort, cost-to-serve, and resolution rate.

### 8.2 Core Patterns

#### Pattern 1: Skills-Based Routing (SBR)

Route contacts to agents based on skills, language, product expertise, or VIP status rather than simply to the next available agent.

```javascript
// Skills-based routing rule configuration
const routingRule = {
  priority: 1,
  condition: 'customer.tier === "vip"',
  action: {
    targetQueue: 'VIP_SUPPORT_QUEUE',
    targetSkills: ['premium_support', customer.language, 'escalation'],
    maxWaitTime: 60,
    overflowTarget: 'VIP_MANAGER_QUEUE'
  }
};

// Non-VIP routing
const standardRouting = {
  priority: 2,
  condition: 'true', // default rule
  action: {
    targetQueue: 'GENERAL_SUPPORT_QUEUE',
    targetSkills: [customer.language, 'standard_support'],
    maxWaitTime: 120,
    overflowTarget: 'BACKUP_QUEUE',
    callbackOfferThreshold: 180 // Offer callback if wait > 3 minutes
  }
};
```

#### Pattern 2: Queue Priority & Urgency Triage

```javascript
// Assign priority based on customer and interaction characteristics
function calculatePriority(callData) {
  let basePriority = 5; // 1 = highest, 10 = lowest
  
  // VIP customers get priority boost
  if (callData.accountTier === 'enterprise') basePriority -= 3;
  else if (callData.accountTier === 'premium') basePriority -= 2;
  
  // Escalated issues get priority boost
  if (callData.isEscalation) basePriority -= 2;
  
  // Long wait so far = priority bump
  if (callData.currentWaitSeconds > 120) basePriority -= 1;
  
  return Math.max(1, Math.min(10, basePriority));
}
```

#### Pattern 3: Virtual Queuing (Callback Option)

Offer customers a callback instead of waiting on hold. This reduces abandonment rates and improves satisfaction.

```
Customer calls → Estimated wait > 2 minutes?
       │
       ├──Yes──► Offer callback: "We can call you back in approximately X minutes"
       │              │
       │              ├── Customer accepts → Collect callback number → Queue callback request
       │              │                                         │
       │              │                                         ▼
       │              │                              Callback assigned to agent at available time
       │              │
       │              └── Customer declines → Remain in queue with updated position
       │
       └──No──► Remain in queue, play estimated wait message
```

#### Pattern 4: Dark Transfer (Consultative Transfer)

Transfer call with context to a specialist without requiring the customer to repeat information.

```javascript
// Dark transfer with full context preservation
async function performDarkTransfer(callId, targetQueue, context) {
  // Preserve all context during transfer
  const transferPayload = {
    conversationId: callId,
    targetQueueId: targetQueue,
    transferType: 'DARK', // No introduction call to receiving agent
    preserveContext: true,
    context: {
      originalQueue: context.originalQueue,
      customerId: context.customerId,
      issueSummary: context.issueSummary,
      attemptedSolutions: context.attemptedSolutions,
      sentimentScore: context.avgSentimentScore,
      transferReason: context.transferReason
    }
  };
  
  await ccassPlatform.transferCall(transferPayload);
}
```

#### Pattern 5: Post-Call Survey Trigger

```javascript
// After call completion, trigger appropriate survey
async function triggerPostCallSurvey(callData) {
  let surveyType = 'standard';
  let surveyChannel = 'sms';
  
  if (callData.disposition === 'complaint') {
    surveyType = 'detailed';
    surveyChannel = 'email'; // More thorough for escalated issues
  } else if (callData.isVipCustomer) {
    surveyType = 'nps';
    surveyChannel = 'email'; // NPS via email has higher completion for VIPs
  } else if (callData.resolvedOnFirstCall) {
    surveyType = 'short'; // CSAT only, quick
  }
  
  await surveyClient.send({
    type: surveyType,
    channel: surveyChannel,
    customerPhone: callData.customerPhone,
    customerEmail: callData.customerEmail,
    callSid: callData.callSid,
    agentId: callData.agentId,
    // Include survey link with pre-filled context
    prefill: {
      agentName: callData.agentName,
      callDate: callData.startTime,
      disposition: callData.disposition
    }
  });
}
```

### 8.3 Multi-Channel Flow Convergence

Modern contact centers handle voice, chat, email, messaging (WhatsApp, SMS), and social in a unified queue. Flow design must handle channel-specific nuances while maintaining a consistent customer experience.

```javascript
// Channel-specific flow considerations
const channelConfig = {
  VOICE: {
    maxWaitBeforeCallbackOffer: 180, // seconds
    estimatedWaitMessage: true,
    queueMusic: true,
    priorityRouting: true,
    screenPopRequired: true
  },
  CHAT: {
    maxWaitBeforeCallbackOffer: 60,
    estimatedWaitMessage: false, // Show "waiting" instead
    queueMusic: false,
    priorityRouting: true,
    screenPopRequired: false // Chat context already visible
  },
  EMAIL: {
    slaTargetHours: 4,
    priorityRouting: false,
    escalationRule: 'escalate_after_24h_unresolved'
  },
  WHATSAPP: {
    maxWaitBeforeEscalation: 30, // minutes
    autoResponseEnabled: true,
    humanHandoffTrigger: ['escalation_keyword', 'explicit_request']
  }
};
```

---

## 9. Real-Time Data Exchange

### 9.1 Why Real-Time Data Matters

Contact centers require real-time data for:

- **Routing decisions** — Updating routing based on real-time queue states
- **Screen pops** — Looking up customer data during call setup
- **Supervisor dashboards** — Live queue and agent status
- **SLA monitoring** — Tracking service levels in real time
- **Fraud detection** — Real-time flagging of anomalous behavior

### 9.2 Webhook Architecture for Real-Time Events

Webhooks are the primary mechanism for CCaaS platforms to push events to external systems:

```javascript
// Webhook payload structure (Genesys Cloud example)
const webhookPayload = {
  topic: 'v2.conversations.{id}.messages',
  version: '1.0',
  timestamp: '2026-04-22T19:15:00Z',
  sequenceNumber: 12345,
  data: {
    conversationId: 'abc-123-def-456',
    participants: [
      { type: 'USER', userId: 'agent-uuid', name: 'Agent Name' },
      { type: 'EXTERNAL', phoneNumber: '+1234567890' }
    ],
    direction: 'INBOUND',
    ani: '+1234567890',
    dnis: '+18005551234',
    queueId: 'queue-uuid',
    startTime: '2026-04-22T19:14:30Z',
    endTime: null,
    disposition: null
  }
};
```

#### Webhook Security Best Practices

- **Validate signatures** — Most platforms sign webhook payloads (e.g., HMAC-SHA256)
- **Verify source IP ranges** — Whitelist platform IPs where possible
- **Respond quickly, process async** — Webhook endpoints should return 200 quickly and process in the background
- **Handle retries** — Platform webhooks typically retry on non-2xx responses; handle idempotently

```javascript
// Webhook handler with signature verification
async function handleCCaaSWebhook(req, res) {
  const signature = req.headers['x-webhook-signature'];
  const timestamp = req.headers['x-webhook-timestamp'];
  
  // Verify signature (example for Twilio)
  const expectedSig = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(`${timestamp}${req.rawBody}`)
    .digest('hex');
  
  if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSig))) {
    return res.status(401).send('Invalid signature');
  }
  
  // Acknowledge quickly
  res.status(200).send('OK');
  
  // Process async (don't block webhook response)
  await queueMessageForProcessing(req.body);
}
```

### 9.3 WebSocket for Real-Time Streaming

For high-frequency, low-latency data (agent state changes, queue updates), WebSocket streams are superior to webhooks:

```javascript
// WebSocket connection manager for real-time CCaaS events
class CCaaSEventStream {
  constructor(platform) {
    this.platform = platform;
    this.subscriptions = new Map();
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
  }
  
  async connect(token) {
    this.ws = new WebSocket(`${this.platform.wsEndpoint}?access_token=${token}`);
    
    this.ws.on('open', () => {
      console.log('WebSocket connected');
      this.reconnectDelay = 1000; // Reset on successful connect
      this.resubscribeAll();
    });
    
    this.ws.on('message', (data) => {
      const event = JSON.parse(data);
      this.handleEvent(event);
    });
    
    this.ws.on('close', () => {
      console.log('WebSocket disconnected, reconnecting...');
      setTimeout(() => this.connect(token), this.reconnectDelay);
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    });
  }
  
  subscribe(topic, handler) {
    this.subscriptions.set(topic, handler);
    this.sendSubscription(topic);
  }
  
  handleEvent(event) {
    const handler = this.subscriptions.get(event.topicName);
    if (handler) {
      handler(event.data);
    }
  }
}

// Common topics to subscribe to
const eventStream = new CCaaSEventStream(genesysCloud);
eventStream.subscribe('v2.users.{id}.routing-status', handleAgentStatusChange);
eventStream.subscribe('v2.conversations.{id}.calls.started', handleCallStarted);
eventStream.subscribe('v2.conversations.{id}.calls.ended', handleCallEnded);
eventStream.subscribe('v2.queues.{id}.statistics', handleQueueMetrics);
```

### 9.4 Real-Time Metrics Pipeline

Building a real-time metrics pipeline for contact center dashboards:

```javascript
// Real-time metrics aggregation pipeline
class MetricsAggregator {
  constructor() {
    this.intervals = new Map(); // queueId -> current interval metrics
    this.aggregationIntervalMs = 30000;
    this.slastThresholdSeconds = 20;
  }
  
  onCallEvent(event) {
    const queueId = event.queueId;
    
    if (!this.intervals.has(queueId)) {
      this.intervals.set(queueId, new QueueIntervalMetrics(queueId));
    }
    
    const interval = this.intervals.get(queueId);
    
    switch (event.type) {
      case 'CALL_OFFERED':
        interval.offered++;
        interval.oldestCallWaitTime = event.waitTime;
        break;
      case 'CALL_ANSWERED':
        interval.answered++;
        interval.serviceLevelCount += (event.waitTime <= this.slastThresholdSeconds) ? 1 : 0;
        break;
      case 'CALL_ABANDONED':
        interval.abandoned++;
        break;
      case 'AGENT_LOGGED_IN':
        interval.staffed++;
        break;
      case 'AGENT_LOGGED_OUT':
        interval.staffed--;
        break;
    }
  }
  
  startPeriodicPublish(publishFn) {
    setInterval(() => {
      for (const [queueId, interval] of this.intervals) {
        const metrics = interval.compute(this.slastThresholdSeconds);
        publishFn(queueId, metrics);
      }
    }, this.aggregationIntervalMs);
  }
}
```

### 9.5 API Rate Limiting & Throttling

When building integration consumers for CCaaS APIs, implement:

1. **Exponential backoff** — On 429 (rate limited) responses, wait exponentially longer before retry
2. **Request queuing** — Don't exceed rate limits by using a token bucket or leaky bucket algorithm
3. **Batching** — Use batch endpoints where available (e.g., Salesforce composite API)
4. **Caching** — Cache CRM lookups to avoid redundant API calls

```javascript
// Token bucket rate limiter for API calls
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.tokens = maxRequests;
    this.maxTokens = maxRequests;
    this.refillRate = maxRequests / windowMs;
    this.lastRefill = Date.now();
  }
  
  async acquire() {
    this.refill();
    if (this.tokens < 1) {
      const waitTime = (1 - this.tokens) / this.refillRate;
      await this.sleep(waitTime);
      this.refill();
    }
    this.tokens -= 1;
  }
  
  refill() {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    this.tokens = Math.min(this.maxTokens, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }
}
```

---

## 10. Integration Testing Strategy

### 10.1 Testing Pyramid for CCaaS Integration

```
                    ▲
                   / \      E2E / Smoke Tests
                  /   \     (Critical paths: screen pop, call routing, CRM log)
                 /─────\    
                /       \   Integration Tests
               /         \  (API contracts, webhook delivery, data sync)
              /───────────\
             /             \ Unit Tests
            /               \ (Individual service functions, transform logic)
           /─────────────────\
```

### 10.2 Unit Testing Integration Logic

```javascript
// Unit test: phone number normalization
describe('phoneNormalization', () => {
  it('converts US 10-digit to E.164', () => {
    expect(normalizeToE164('(555) 123-4567', 'US')).toBe('+15551234567');
  });
  it('handles already-E.164 numbers', () => {
    expect(normalizeToE164('+442071234567', 'GB')).toBe('+442071234567');
  });
  it('returns null for invalid numbers', () => {
    expect(normalizeToE164('abc', 'US')).toBe(null);
  });
});

// Unit test: CRM lookup response mapping
describe('crmLookupResponseMapping', () => {
  it('maps Salesforce response to screen pop attributes', () => {
    const sfResponse = {
      Id: '003xx000003Ghi1',
      FirstName: 'Jane',
      LastName: 'Doe',
      Phone: '+15551234567',
      Account: { Name: 'Acme Corp', Type: 'Enterprise' }
    };
    const mapped = mapToScreenPopAttributes(sfResponse);
    expect(mapped.customerName).toBe('Jane Doe');
    expect(mapped.accountTier).toBe('Enterprise');
  });
});

// Unit test: disposition code mapping
describe('dispositionMapping', () => {
  const testCases = [
    { ccassCode: 'RESOLVED', expectedSfStatus: 'Completed', expectedCaseUpdate: true },
    { ccassCode: 'ESCALATED', expectedSfStatus: 'Completed', expectedCaseUpdate: true },
    { ccassCode: 'DROPPED', expectedSfStatus: 'Completed', expectedCaseUpdate: false }
  ];
  testCases.forEach(({ ccassCode, expectedSfStatus }) => {
    it(`maps ${ccassCode} → Salesforce ${expectedSfStatus}`, () => {
      expect(mapDisposition(ccassCode).sfStatus).toBe(expectedSfStatus);
    });
  });
});
```

### 10.3 Integration Testing with Mocks

```javascript
// Integration test: Salesforce CRM lookup via mock server
describe('CRM Integration: Screen Pop Lookup', () => {
  let mockSalesforceServer;
  
  beforeAll(async () => {
    mockSalesforceServer = await MockSalesforceServer.start({
      port: 3001,
      searchResponse: {
        totalSize: 1,
        records: [{
          Id: 'contact-123',
          attributes: { type: 'Contact' },
          FirstName: 'Jane',
          LastName: 'Doe',
          Phone: '+15551234567'
        }]
      }
    });
  });
  
  afterAll(() => mockSalesforceServer.close());
  
  it('looks up contact by ANI and returns screen pop data', async () => {
    const result = await performScreenPopLookup('+15551234567');
    
    expect(result.found).toBe(true);
    expect(result.contactId).toBe('contact-123');
    expect(result.name).toBe('Jane Doe');
    expect(mockSalesforceServer.receivedRequests).toHaveLength(1);
    expect(mockSalesforceServer.receivedRequests[0].path).toContain('/search/');
  });
  
  it('handles contact-not-found gracefully', async () => {
    const result = await performScreenPopLookup('+15559999999');
    
    expect(result.found).toBe(false);
    expect(result.action).toBe('create_lead');
  });
  
  it('times out and falls back after CRM timeout', async () => {
    mockSalesforceServer.setDelay(5000); // Delay beyond timeout threshold
    
    const result = await performScreenPopLookup('+15551234567', { timeout: 1000 });
    
    expect(result.found).toBe(null);
    expect(result.action).toBe('fallback_timeout');
    expect(result.fallbackUrl).toContain('/new-contact?ani=');
  });
});
```

### 10.4 Contract Testing

Contract testing ensures that both the CCaaS platform and the consuming system agree on API interfaces. Use Pact for consumer-driven contract testing:

```javascript
// Pact contract: CRM lookup consumer
const { Pact } = require('@pact-foundation/pact');
const provider = new Pact({
  consumer: 'CCaaS_Platform',
  provider: 'Salesforce_CRM'
});

describe('Salesforce CRM Contract', () => {
  beforeEach(() => provider.addInteraction({
    state: 'Contact with phone +15551234567 exists',
    uponReceiving: 'a request to search for contact by phone',
    withRequest: {
      method: 'POST',
      path: '/services/data/v59.0/search',
      headers: { 'Authorization': 'Bearer test-token', 'Content-Type': 'application/json' },
      body: { query: /Phone.*\+15551234567/ }
    },
    willRespondWith: {
      status: 200,
      body: {
        totalSize: 1,
        records: Matchers.eachLike({
          Id: Matchers.string('contact-123'),
          FirstName: Matchers.string('Jane'),
          LastName: Matchers.string('Doe'),
          Phone: Matchers.string('+15551234567')
        })
      }
    }
  }));
  
  it('returns contact when searching by phone', async () => {
    const result = await callSalesforceSearch('+15551234567');
    expect(result.records).toHaveLength(1);
  });
});
```

### 10.5 End-to-End (E2E) Testing

E2E tests validate complete flows across all integrated systems:

```javascript
// E2E test: Complete inbound call flow
describe('E2E: Inbound Call with Screen Pop and Activity Log', () => {
  it('complete flow: call arrives → screen pop → call ends → activity logged in Salesforce', async () => {
    // Step 1: Simulate inbound call with ANI
    const call = await testCCaaS.simulateInboundCall({
      from: '+15551234567',
      to: '+18005551234',
      flowId: TEST_FLOW_ID
    });
    expect(call.status).toBe('ringing');
    
    // Step 2: Wait for screen pop event (poll / webhook)
    const screenPopEvent = await waitForEvent('screenPop', { timeoutMs: 5000 });
    expect(screenPopEvent.found).toBe(true);
    expect(screenPopEvent.url).toContain('salesforce.com');
    
    // Step 3: Agent answers call
    await testCCaaS.answerCall(call.callId, 'AGENT_001');
    
    // Step 4: Simulate wrap-up (agent marks disposition)
    await testCCaaS.completeCall(call.callId, {
      disposition: 'RESOLVED',
      notes: 'Customer inquiry answered successfully'
    });
    
    // Step 5: Verify activity was logged in Salesforce
    await waitForCondition(async () => {
      const activities = await testSalesforce.getTasksForContact(screenPopEvent.contactId);
      return activities.find(a => 
        a.CallObject === call.callId && 
        a.Status === 'Completed'
      );
    }, { timeoutMs: 10000, intervalMs: 500 });
    
    // Assert: activity exists
    const loggedActivity = await testSalesforce.getTaskByCallObject(call.callId);
    expect(loggedActivity.Subject).toContain('Inbound Call');
    expect(loggedActivity.Description).toContain('Customer inquiry answered');
  });
});
```

### 10.6 Testing Strategy by Environment

| Environment | Purpose | Data | Testing Scope |
|------------|---------|------|--------------|
| Local / Dev | Unit tests, local integration | Mocked data | Logic + basic contracts |
| Sandbox / Dev | Integration testing | Sanitised production-like | Full API integration |
| Staging / QA | E2E testing, UAT | Synthetic data, anonymised production | Complete flows |
| Production | Smoke tests, monitoring | Production | Critical path monitoring only |

### 10.7 Testing Checklist

- [ ] Unit tests for all data transformation logic
- [ ] Contract tests for every external API (CRM, WFM, QM)
- [ ] Integration tests with mocked external systems
- [ ] E2E tests covering the critical path (call → screen pop → CRM update → call end)
- [ ] Webhook delivery and signature verification tests
- [ ] Timeout and error handling tests (CRM offline, slow response)
- [ ] Rate limiting tests (ensure graceful degradation)
- [ ] Data privacy tests (PII handling, token masking in logs)
- [ ] Performance tests (API response times under load)
- [ ] Rollback/rollback simulation tests (what happens if integration breaks)

---

## Appendix: API Quick Reference

### A.1 Genesys Cloud API Base URLs

| Environment | Base URL |
|-------------|----------|
| Production (US) | `https://api.mypurecloud.com` |
| Production (EU) | `https://api.mypurecloud.de` |
| Production (APAC) | `https://api.mypurecloud.com.au` |

### A.2 Twilio Flex API Base

| Resource | Base URL |
|----------|----------|
| TaskRouter | `https://taskrouter.twilio.com` |
| Studio | `https://studio.twilio.com` |
| Sync | `https://sync.twilio.com` |
| Functions | Serverless (account-scoped) |

### A.3 Common HTTP Headers

```
Authorization: Bearer {OAUTH_TOKEN}
Content-Type: application/json
Accept: application/json
X-Api-Version: v59.0  (Salesforce)
```

### A.4 Webhook Security Headers Reference

| Platform | Header | Algorithm |
|----------|--------|-----------|
| Twilio | `X-Twilio-Signature` | HMAC-SHA1 |
| Genesys | `X-Auth-Token` | Bearer Token |
| HubSpot | `Authorization: Bearer {token}` | OAuth 2.0 |
| Salesforce | `Authorization: Bearer {token}` | OAuth 2.0 |

### A.5 Common CCaaS Event Types

| Event | Genesys Topic | Twilio Event | Trigger |
|-------|--------------|--------------|---------|
| Call started | `v2.conversations.{id}.calls.started` | `task.created` | Inbound call arrives |
| Call answered | `v2.conversations.{id}.calls.answered` | `task.accepted` | Agent answers |
| Call ended | `v2.conversations.{id}.calls.ended` | `task.completed` | Call terminates |
| Agent available | `v2.users.{id}.routing-status` | `worker.activity.update` | Agent status change |
| Queue updated | `v2.queues.{id}.statistics` | `taskQueue.updated` | Queue metrics change |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-09-12 | CXaaS Specialist | Initial draft — CTI and CRM integration |
| 2.0 | 2025-01-28 | CXaaS Specialist | Added WFM integration, QM section, contact flows |
| 3.0 | 2026-04-22 | CXaaS Specialist | Comprehensive rewrite — all sections expanded, integration testing added |

---

*This document is maintained by the CXaaS Specialist agent within the OpenClaw hive. For questions, updates, or additions, contact the specialist or update the file directly at `~/.openclaw/hive/agents/cxaas-specialist/learnings/integration-v3.md`.*