# MediRoute AI - Backend

Autonomous Medical Evacuation Decision Engine

## Overview

MediRoute AI is an intelligent medical emergency routing system that uses a multi-agent architecture to process emergency requests, verify insurance, match patients with appropriate hospitals, and generate Letters of Authorization (LOA) for immediate care.

## Architecture Overview

MediRoute AI uses a **multi-agent orchestration** pattern built with LangGraph. The system routes patient requests through specialized agents that handle verification, classification, hospital matching, LOA generation, and response formatting. The orchestrator intelligently determines the workflow path based on user intent and emergency severity.

---

## 🚀 Production Readiness & Scaling Assessment

### Current Architecture Analysis

#### Strengths ✅
1. **Well-structured multi-agent system** using LangGraph for orchestration
2. **Separation of concerns** - each agent has a clear, single responsibility
3. **Stateful conversation management** - supports both single-shot and chat modes
4. **Streaming capabilities** - real-time responses for better UX
5. **Insurance verification with benefit tracking** - comprehensive validation
6. **Intelligent hospital matching** - filters by insurance, capabilities, and distance
7. **Severity-based routing** - CRITICAL auto-selects, non-critical offers choices

---

### Current Limitations & How to Fix Them 🔧

#### 1. **Mock Data Sources**
- **Problem:** Hospitals, insurance records, and doctors are hardcoded in Python dictionaries
- **Impact:** Not scalable, data inconsistency, no audit trail
- **Solution:** Migrate to PostgreSQL with proper relational schema, indexes, and foreign keys
- **Benefits:** Data integrity, ACID compliance, ability to handle millions of records, audit logging

#### 2. **Mock Geocoding**
- **Problem:** Only 13 hardcoded Philippine locations supported
- **Impact:** Limited coverage, inaccurate distance calculations (straight-line vs. actual driving)
- **Solution:** Integrate Google Maps Geocoding API and Distance Matrix API
- **Benefits:** Any address supported, real-time traffic data, accurate ETAs, no need to ask location if GPS-enabled

#### 3. **No Persistent Storage**
- **Problem:** Session state stored in memory, lost on restart
- **Impact:** Users lose conversation history, can't resume sessions
- **Solution:** Store session state in Redis or PostgreSQL
- **Benefits:** Session persistence, analytics, compliance (audit trail)

#### 4. **Single LLM Provider**
- **Problem:** Vendor lock-in, no fallback if provider fails
- **Impact:** Service downtime, cost inflexibility
- **Solution:** Abstract LLM interface to support multiple providers (OpenAI, Anthropic, Google, Azure)
- **Benefits:** Redundancy, cost optimization, A/B testing different models

#### 5. **No Monitoring/Observability**
- **Problem:** Can't track performance, errors, or bottlenecks in production
- **Impact:** Blind to issues, slow incident response
- **Solution:** Implement Prometheus (metrics), Grafana (dashboards), Jaeger (tracing), Sentry (errors)
- **Benefits:** Proactive issue detection, performance optimization, SLA tracking

#### 6. **No Rate Limiting**
- **Problem:** Vulnerable to abuse, DDoS attacks, runaway costs
- **Impact:** Service degradation, unexpected bills
- **Solution:** Implement rate limiting per IP/user (e.g., 10 requests/minute)
- **Benefits:** Fair usage, cost control, protection against abuse

#### 7. **No Authentication/Authorization**
- **Problem:** Open endpoints, anyone can access
- **Impact:** Data privacy violations, unauthorized access
- **Solution:** Implement JWT tokens, API keys, role-based access control (RBAC)
- **Benefits:** Secure access, compliance with healthcare regulations (HIPAA, Data Privacy Act)

#### 8. **Basic Error Handling**
- **Problem:** Generic error messages, poor graceful degradation
- **Impact:** Poor user experience, hard to debug issues
- **Solution:** Implement retry logic, circuit breakers, detailed error responses
- **Benefits:** Better UX, easier troubleshooting, resilience

---

## 📋 Future Enhancement Recommendations

### 🌍 1. Location Intelligence & Automation

**Current State:**
- Mock geocoding with 13 hardcoded locations
- Straight-line distance calculation (Haversine)
- User must manually type location

**Future Improvements:**
- **Google Maps Integration:** Accurate geocoding for any Philippine address
- **Real-time Traffic Data:** ETA with current traffic conditions, not just distance
- **Auto-location Detection:** GPS from mobile devices → orchestrator skips asking
- **Route Optimization:** Suggest fastest route considering traffic, not just nearest hospital

**Impact:**
- Faster emergency response times
- Better hospital recommendations based on actual travel time
- Reduced user friction (no typing during emergency)
- Nationwide coverage, not just Metro Manila

---

### 🎙️ 2. Voice Modality (Speech Interface)

**Current State:**
- Text-only chatbot
- Requires typing on mobile/desktop

**Future Improvements:**
- **Speech-to-Text (STT):** Users speak their emergency (Whisper API or Google Speech)
- **Text-to-Speech (TTS):** Voice responses for hands-free interaction
- **Multi-language Support:** English, Tagalog, Cebuano, Ilocano
- **Streaming Audio:** Real-time voice responses as agent processes

**Impact:**
- Critical for hands-free scenarios (driving, physical incapacitation)
- Accessibility for elderly, visually impaired, low literacy
- Faster input than typing during emergencies
- More natural, conversational experience

---

### 🏥 3. Real-time Hospital Integration

**Current State:**
- Static hospital data (capacity, capabilities)
- No live availability information

**Future Improvements:**
- **Bed Availability API:** Real-time ER, ICU, general bed counts
- **Equipment Status:** Availability of CT scan, MRI, ventilators
- **Staff on Duty:** Specialists currently available
- **Wait Time Estimates:** Current ER queue length
- **Direct LOA Transmission:** Send LOA to hospital system automatically

**Impact:**
- Avoid sending patients to full hospitals
- Better resource allocation during surges
- Reduced hospital turnaround time (LOA pre-sent)
- Data-driven capacity planning

---

### 🚀 4. Scaling Architecture

**Current State:**
- Single-server deployment
- In-memory state
- Synchronous processing

**Future Infrastructure:**

#### Database Layer
- **PostgreSQL:** Relational data (insurance, hospitals, doctors, claims)
- **Redis:** Session caching, hospital match caching, rate limiting
- **Read Replicas:** Distribute read load for hospital searches
- **Geospatial Indexing:** Fast location-based queries

#### Application Layer
- **Containerization:** Docker for consistent deployments
- **Load Balancing:** Nginx/ALB distributing traffic across multiple instances
- **Auto-scaling:** Scale up during peak hours (evenings, weekends)
- **Message Queue:** Celery/RabbitMQ for async tasks (email LOA, SMS notifications)

#### Monitoring & Observability
- **Prometheus + Grafana:** Metrics and dashboards
- **Jaeger:** Distributed tracing across agents
- **Sentry:** Error tracking and alerting
- **ELK Stack:** Centralized logging for debugging
- **PagerDuty:** Incident management and on-call rotation

**Impact:**
- Handle 10,000+ concurrent users
- 99.9% uptime SLA
- Fast incident response
- Cost-efficient auto-scaling

---

### 🔐 5. Security & Compliance

**Current State:**
- No authentication
- No encryption
- No audit trails

**Future Requirements:**

#### Authentication & Authorization
- **JWT Tokens:** Session management
- **API Keys:** Partner/hospital integration
- **OAuth 2.0:** SSO with insurance provider systems
- **RBAC:** Different permissions for patients, doctors, hospitals, admins

#### Data Protection
- **HTTPS/TLS:** All traffic encrypted
- **Data Encryption at Rest:** Database encryption
- **PII Masking:** Sensitive data redaction in logs
- **GDPR/Data Privacy Act Compliance:** Right to deletion, data portability

#### Security Hardening
- **Rate Limiting:** Prevent brute force, DDoS
- **Input Validation:** Prevent SQL injection, prompt injection
- **WAF:** Web Application Firewall for attack prevention
- **Security Audits:** Regular penetration testing

**Impact:**
- Protect patient privacy (legal requirement)
- Build trust with users and partners
- Avoid data breaches and penalties
- Enable enterprise adoption

---

### 💡 6. Advanced AI Capabilities

**Current State:**
- Rule-based severity classification
- Static LLM prompts
- Single LLM provider

**Future Enhancements:**

#### Multi-provider LLM Strategy
- **OpenAI:** Primary for structured outputs (classification, LOA)
- **Anthropic Claude:** Fallback, better at medical reasoning
- **Google Gemini:** Cost-effective for simple queries
- **Fine-tuned Models:** Custom model for Philippine medical context

#### Intelligent Features
- **Predictive Triage:** ML model predicts severity from symptoms + patient history
- **Anomaly Detection:** Flag unusual patterns (fraud, emergencies)
- **Personalization:** Recommendations based on patient history, preferences
- **Multi-language NLU:** Understand code-switching (Taglish)

**Impact:**
- Better accuracy in emergency classification
- Reduced LLM costs (right model for right task)
- Resilience (fallback if primary provider fails)
- Localized to Philippine healthcare context

---

### 📱 7. Multi-channel Support

**Current State:**
- Web chatbot only

**Future Channels:**
- **Mobile App:** Native iOS/Android with push notifications
- **SMS Gateway:** Text-based access for low-connectivity areas
- **WhatsApp/Viber:** Popular messaging platforms in Philippines
- **Voice Hotline:** Phone-based access with voice AI
- **Wearables:** Integration with Apple Watch, Fitbit for emergency triggers

**Impact:**
- Reach users regardless of device/connectivity
- Critical for rural/underserved areas
- Better emergency accessibility
- Wider market reach

---

### 📊 8. Analytics & Business Intelligence

**Current State:**
- No analytics, no insights

**Future Capabilities:**
- **Operational Dashboard:** Real-time emergency volume, response times
- **Hospital Utilization:** Which hospitals are over/under capacity
- **Insurance Analytics:** Claim patterns, fraud detection
- **Geographic Heatmaps:** Emergency hotspots by location/time
- **Predictive Analytics:** Forecast demand surges (flu season, disasters)

**Impact:**
- Data-driven decision making
- Resource optimization (ambulance positioning)
- Cost reduction through fraud detection
- Proactive capacity planning

---

## 💰 Cost Optimization Strategies

### LLM Costs
- **Tiered Model Usage:** Small models for simple tasks, large for complex
- **Response Caching:** Cache FAQ, common scenarios
- **Prompt Optimization:** Reduce token count without sacrificing quality
- **Batch Processing:** Group non-urgent requests

### Infrastructure Costs
- **Auto-scaling:** Scale down during low-traffic hours
- **Spot Instances:** Use for non-critical background jobs
- **CDN:** Reduce server load for static assets
- **Database Optimization:** Proper indexing, query optimization

### API Costs (Google Maps, etc.)
- **Geocoding Cache:** Cache results (addresses don't change often)
- **Batch Requests:** Combine multiple distance calculations
- **Fallback to Free Tier:** Use OpenStreetMap for non-critical features

---

## 📈 Scaling Strategy: From Prototype to Production

### Stage 1: MVP (Current - 100 users/day)
- Single server
- Mock data
- Basic chat interface
- Manual testing

### Stage 2: Beta (1,000 users/day)
- PostgreSQL database
- Google Maps integration
- Redis caching
- Basic monitoring
- Rate limiting

### Stage 3: Production Launch (10,000 users/day)
- Load balancing (3+ servers)
- Auto-scaling
- Full monitoring stack
- Security hardening
- 24/7 support

### Stage 4: Scale (100,000+ users/day)
- Multi-region deployment
- CDN for global access
- Database sharding
- Advanced caching (edge)
- ML-based optimizations

---

## 🎯 Implementation Priority Matrix

### Must-Have (Before Production Launch)
1. **Database Migration** - Replace mock data with PostgreSQL
2. **Google Maps API** - Accurate location and distance
3. **Rate Limiting & Security** - Protect against abuse
4. **Basic Monitoring** - Track uptime and errors
5. **Error Handling** - Graceful degradation

### High-Value Additions (First 6 Months)
1. **Voice Modality** - Hands-free emergency reporting
2. **Redis Caching** - Improve performance
3. **Multi-provider LLM** - Reduce costs and risks
4. **Hospital Integration** - Real-time bed availability
5. **Mobile App** - Native experience

### Future Innovations (6-12 Months)
1. **Predictive Analytics** - ML-based triage
2. **Multi-language Support** - Tagalog, Cebuano, etc.
3. **Ambulance Integration** - Dispatch coordination
4. **Wearable Integration** - Automatic emergency detection
5. **Telemedicine** - Virtual doctor consultation

---

## 📊 Success Metrics & KPIs

### Operational KPIs
- **Response Time:** < 5 seconds for hospital match
- **Uptime:** 99.9% availability
- **Error Rate:** < 0.5%
- **Concurrent Users:** Support 10,000+

### Business KPIs
- **LOA Success Rate:** > 90% (approved and used)
- **Hospital Match Accuracy:** > 85% patient satisfaction
- **User Retention:** > 60% return users
- **Average Session Time:** Track efficiency

### Cost KPIs
- **LLM Cost per Session:** < $0.10
- **Infrastructure Cost:** < $1,000/month for 10K users
- **Customer Acquisition Cost:** Track marketing efficiency

---

**Recommended Next Steps:**  
Focus on database migration and Google Maps integration first. These two changes provide the foundation for all other improvements and make the system production-viable.

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
