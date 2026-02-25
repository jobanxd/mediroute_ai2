# MediRoute AI - Backend

Autonomous Medical Evacuation Decision Engine

## Overview

MediRoute AI is an intelligent medical emergency routing system that uses a multi-agent architecture to process emergency requests, verify insurance, match patients with appropriate hospitals, and generate Letters of Authorization (LOA) for immediate care.

## Agentic Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              START: User Message                             │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   ORCHESTRATOR AGENT          │
                    │   - Analyzes user intent      │
                    │   - Routes to appropriate     │
                    │     agent or responds         │
                    │   - Tool: call_verification   │
                    │   - Tool: call_loa_agent      │
                    └──┬─────────────────────────┬──┘
                       │                         │
              ┌────────┴────────┐                │
              │ General Q&A?    │                │
              │ (No Emergency)  │                │
              └────────┬────────┘                │
                       │                         │
                       ▼                         │
                   ┌───────┐                     │
                   │  END  │                     │
                   └───────┘                     │
                                                 │
              ┌──────────────────────────────────┴─────────────────────┐
              │                                                         │
              ▼                                                         ▼
┌─────────────────────────────┐                        ┌─────────────────────────────┐
│   VERIFICATION AGENT        │                        │   LOA AGENT (Direct)        │
│   - Verifies patient        │                        │   - User already chose      │
│   - Checks insurance        │                        │     hospital from top 3     │
│   - Validates policy        │                        │   - Generates LOA           │
│   - Calculates remaining    │                        │   - Assigns doctor          │
│     benefits (history)      │                        │   - Approves services       │
└──────────┬──────────────────┘                        └──────────┬──────────────────┘
           │                                                       │
           │                                                       │
    ┌──────┴──────┐                                               │
    │  Verified?  │                                               │
    └──────┬──────┘                                               │
           │                                                       │
     ┌─────┴─────┐                                                │
     │           │                                                 │
     │ NO        │ YES                                            │
     │           │                                                 │
     ▼           ▼                                                 │
┌─────────┐  ┌─────────────────────────────┐                    │
│Response │  │  CLASSIFICATION AGENT        │                    │
│ Agent   │  │  - Extracts symptoms         │                    │
│ (Error) │  │  - Classifies emergency type │                    │
└─────────┘  │    (CARDIAC, TRAUMA, etc.)   │                    │
             │  - Assesses severity         │                    │
             │  - Determines dispatch need  │                    │
             │  - Recommends action         │                    │
             └──────────┬──────────────────┘                    │
                        │                                         │
                        ▼                                         │
        ┌─────────────────────────────┐                         │
        │   MATCH AGENT                │                         │
        │   - Filters hospitals by:    │                         │
        │     • Insurance acceptance   │                         │
        │     • Required capabilities  │                         │
        │     • Distance (max 50km)    │                         │
        │   - Ranks by distance        │                         │
        │   - Two modes:               │                         │
        │     1. CRITICAL → Auto-select│                         │
        │     2. Non-Critical → Top 3  │                         │
        └──────────┬──────────────────┘                         │
                   │                                              │
            ┌──────┴──────┐                                      │
            │   Severity   │                                      │
            └──────┬───────┘                                      │
                   │                                              │
         ┌─────────┴─────────┐                                   │
         │                   │                                    │
         ▼                   ▼                                    │
   ┌──────────┐      ┌──────────────┐                           │
   │ CRITICAL │      │ NON-CRITICAL │                           │
   │          │      │              │                            │
   │ Auto-    │      │ Present      │                            │
   │ Select   │      │ Top 3        │                            │
   │ Closest  │      │ Options      │                            │
   └────┬─────┘      └──────┬───────┘                           │
        │                   │                                    │
        │                   ▼                                    │
        │            ┌─────────────┐                            │
        │            │ User Selects│                            │
        │            │ Hospital    │                            │
        │            └──────┬──────┘                            │
        │                   │                                    │
        └───────────────────┴────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────┐
            │   LOA AGENT                  │
            │   - Generates LOA number     │
            │   - Assigns doctor by        │
            │     specialization           │
            │   - Approves services based  │
            │     on hospital capabilities │
            │   - Creates clinical         │
            │     justification            │
            │   - Sets validity (48h)      │
            └──────────┬──────────────────┘
                       │
                       ▼
       ┌─────────────────────────────┐
       │   REPORT AGENT               │
       │   - Compiles all data        │
       │   - Structures final report  │
       │   - Includes:                │
       │     • Classification         │
       │     • Verification           │
       │     • Hospital match         │
       │     • LOA details            │
       │     • Benefit tracking       │
       └──────────┬──────────────────┘
                  │
                  ▼
  ┌─────────────────────────────┐
  │   RESPONSE AGENT             │
  │   - Generates natural        │
  │     language response        │
  │   - Formats for UI display   │
  │   - Provides next steps      │
  └──────────┬──────────────────┘
             │
             ▼
        ┌─────────┐
        │   END   │
        └─────────┘
```

### Agent Responsibilities

#### 1. **Orchestrator Agent**
- **Purpose**: Entry point that analyzes user intent and routes appropriately
- **Tools**: 
  - `call_verification_agent` - For emergency admission requests
  - `call_loa_agent` - When user has already selected a hospital
- **Outputs**: Routes to verification, LOA, or provides direct response

#### 2. **Verification Agent**
- **Purpose**: Validates patient identity and insurance eligibility
- **Checks**:
  - Policy number existence and status
  - Policy validity dates
  - Patient name and DOB match
  - Insurance benefit usage history
- **Outputs**: Insurance details, remaining benefits, verification status

#### 3. **Classification Agent**
- **Purpose**: Medical triage and classification
- **Classifications**: CARDIAC, TRAUMA, RESPIRATORY, NEUROLOGICAL, BURNS, GENERAL
- **Severity Levels**: CRITICAL, URGENT, MODERATE
- **Outputs**: Emergency type, severity, dispatch requirement, recommended action

#### 4. **Match Agent**
- **Purpose**: Find and rank appropriate hospitals
- **Filters**:
  - Insurance acceptance (GlobalCare, AIA, Insular Life)
  - Required medical capabilities (trauma unit, ICU, etc.)
  - Maximum distance (50km radius)
- **Ranking**: By distance (closest first)
- **Modes**:
  - **CRITICAL**: Auto-selects closest matching hospital
  - **Non-CRITICAL**: Presents top 3 options for user selection

#### 5. **LOA Agent**
- **Purpose**: Generate Letter of Authorization
- **Functions**:
  - Assigns specialist doctor based on classification
  - Approves services based on hospital capabilities
  - Creates clinical justification using LLM
  - Sets 48-hour validity period
- **Outputs**: Complete LOA with authorization details

#### 6. **Report Agent**
- **Purpose**: Compile comprehensive report
- **Consolidates**:
  - All agent outputs
  - Patient information
  - Hospital details
  - LOA authorization
  - Insurance benefit status

#### 7. **Response Agent**
- **Purpose**: Generate user-friendly natural language response
- **Formats**: Final output for UI display with next steps

### Key Features

- 🏥 **Multi-Hospital Network**: 10+ hospitals across Metro Manila
- 💳 **Insurance Integration**: GlobalCare, AIA Philippines Life, Insular Life
- 🚑 **Smart Dispatch Logic**: Automatic ambulance routing for critical cases
- 📊 **Benefit Tracking**: Real-time insurance usage calculation
- 🗺️ **Geo-Matching**: Distance-based hospital ranking with 50km radius
- 👨‍⚕️ **Doctor Assignment**: Automatic specialist matching by emergency type
- ⏱️ **48-Hour LOA Validity**: Immediate authorization for emergency care

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Setup and Installation

1. **Navigate to the app folder**
   ```bash
   cd app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your required API keys and configuration.

## Running the Application

**Start the development server:**
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

- `GET /health` - Health check endpoint
- See http://localhost:8000/docs for full API documentation

## Development

The `--reload` flag enables auto-reload on code changes during development.

To run without auto-reload (production-like):
```bash
uvicorn main:app
```
