# Chinese Auto Parts Price Bot - Open Questions Documentation

## 1. Purpose

Open questions are tracked to reduce project risk, align all stakeholders on key decisions, and finalize the project scope before beginning code development. These questions represent critical decisions that will impact system architecture, user experience, and development timeline. Resolving these questions ensures we have a complete and actionable project brief before moving to implementation.

## 2. Categorized Questions

### Data & Sources

- **Initial Parts Database**: What will be the initial source of the parts database?
  - Manual Excel entry with sample data
  - Automated scraping from existing sources
  - Hybrid approach with curated sample data + scraping
  - Third-party data provider integration

- **Price Update Frequency**: How often will prices be updated and who manages this process?
  - Daily, weekly, or on-demand updates
  - Manual admin updates vs automated processes
  - Price validity periods and expiration handling

- **Seller Integration**: Should sellers have direct access to provide/update prices?
  - Seller portal for price submissions
  - API access for automated price updates
  - Manual admin-only price management

- **Data Quality Control**: How do we ensure data accuracy and consistency?
  - Validation rules for OEM codes and part specifications
  - Deduplication processes for similar parts
  - Quality assurance workflows

### Bot & User Experience

- **Bulk Query Limits**: What is the maximum number of lines/items allowed per bulk request?
  - Technical limit (5, 10, 20, 50 items)
  - Business logic considerations
  - User experience impact

- **File Upload Support**: Should the bot support file uploads (CSV/TXT) in addition to text input?
  - CSV file parsing for bulk queries
  - Text file upload capabilities
  - File size and format restrictions

- **Confirmation Requirements**: Should confirmation always be required, or can "trusted" queries skip it?
  - Always require confirmation for data capture
  - Skip confirmation for repeat customers
  - Confidence-based confirmation (high confidence = skip)

- **Multi-language Support**: Should the bot support multiple languages beyond Persian in the future?
  - English support for international users
  - Arabic support for regional markets
  - Language detection and switching

- **Search Result Display**: How should search results be presented to users?
  - Single best match with confirmation
  - Multiple options with selection
  - Detailed part specifications in results

### Orders & Leads

- **Order Reference Numbers**: Should each order get a unique reference number visible to the user?
  - Format: ORD-12345, #12345, or custom format
  - Reference number generation algorithm
  - User communication of reference numbers

- **Repeat Customer Handling**: How should repeat customers be handled?
  - Automatic linking to previous lead records
  - Customer history and preferences
  - Loyalty program considerations

- **Order Notifications**: Do we need automated notifications when orders are created?
  - SMS notifications to customers
  - Telegram notifications to admin team
  - Email confirmations and updates

- **Order Status Updates**: How should customers be notified of order status changes?
  - Telegram messages for status updates
  - Customer-initiated status checking
  - Admin-initiated customer communication

- **Lead Data Retention**: How long should we retain customer data?
  - GDPR compliance considerations
  - Data retention policies
  - Customer data deletion processes

### Admin Panel

- **SPA Framework Selection**: Which SPA framework should we finalize?
  - Nuxt.js for SSR capabilities
  - Vue.js + Vite for development speed
  - Quasar Framework for UI components
  - React + Next.js alternative

- **Role-Based Dashboards**: Do we need role-based dashboards with different views?
  - Admin: Full system access and configuration
  - Operator: Order and customer management focus
  - Manager: Reporting and oversight capabilities
  - Customizable dashboard layouts

- **Reporting & Analytics**: Should the panel include reporting/analytics capabilities?
  - Orders per week/month statistics
  - Top searched parts analysis
  - Customer conversion metrics
  - Revenue and performance dashboards

- **Admin Panel Authentication**: How should admin panel authentication be implemented?
  - JWT tokens with refresh mechanism
  - Session-based authentication
  - Two-factor authentication requirements
  - Password reset and recovery flows

- **Real-time Updates**: Should the admin panel support real-time updates?
  - WebSocket connections for live order updates
  - Polling for data refresh
  - Push notifications for critical events

### AI Search

- **AI Implementation**: Will AI use local embeddings or an external API?
  - Local embedding models (faster, offline)
  - External APIs (OpenAI, Google, etc.)
  - Hybrid approach with fallback options
  - Cost and performance considerations

- **AI Error Handling**: How should AI errors/fallbacks be logged and monitored?
  - Error logging and alerting systems
  - Fallback to basic search mechanisms
  - Performance monitoring and optimization
  - User experience during AI failures

- **Auto-synonym Generation**: Should AI also handle synonyms auto-generation?
  - Automatic keyword extraction from part descriptions
  - Persian synonym generation
  - Quality control for auto-generated synonyms
  - Manual review and approval process

- **AI Training Data**: What training data will be used for the AI model?
  - Existing parts database
  - External automotive terminology
  - Persian language automotive terms
  - Continuous learning from user queries

### Technical & Infrastructure

- **Rate Limiting Strategy**: Should rate-limiting be per user, per IP, or both?
  - Per telegram_user_id limiting
  - Per IP address limiting
  - Combined approach with different limits
  - Rate limit configuration and adjustment

- **Monitoring & Observability**: What is the minimum viable monitoring/observability setup?
  - Application performance monitoring
  - Database performance metrics
  - Error tracking and alerting
  - User behavior analytics

- **Database Migration Timeline**: When to move from SQLite → Postgres?
  - Migration trigger criteria (user count, data size)
  - Migration process and downtime considerations
  - Data backup and rollback procedures
  - Performance testing and validation

- **Backup Strategy**: Should backups be manual or automated?
  - Daily automated backups via systemd timers
  - Manual backup procedures
  - Backup storage location and retention
  - Disaster recovery procedures

- **SSL & Security**: What SSL and security measures are needed?
  - Let's Encrypt certificate management
  - Caddy reverse proxy configuration
  - API security headers and CORS
  - Database encryption at rest

- **Deployment Process**: What is the deployment and update process?
  - Zero-downtime deployment procedures
  - Database migration during updates
  - Rollback procedures for failed deployments
  - Environment management (dev, staging, prod)

## 3. Prioritization

| Question | Category | Priority | Notes |
|----------|----------|----------|-------|
| Initial Parts Database | Data & Sources | **High** | Blocks development start |
| Bulk Query Limits | Bot & UX | **High** | Affects user flow design |
| AI Implementation | AI Search | **High** | Core feature dependency |
| SPA Framework Selection | Admin Panel | **High** | Affects development timeline |
| Order Reference Numbers | Orders & Leads | **Medium** | Important for user experience |
| Price Update Frequency | Data & Sources | **Medium** | Operational requirement |
| Role-Based Dashboards | Admin Panel | **Medium** | Affects admin panel scope |
| Multi-language Support | Bot & UX | **Low** | Future enhancement |
| File Upload Support | Bot & UX | **Low** | Nice-to-have feature |
| Auto-synonym Generation | AI Search | **Low** | Advanced AI feature |

## 4. Decision Matrix

### High Priority Decisions Needed Before Development

1. **Initial Data Source** (Data & Sources)
   - **Owner**: Product Owner
   - **Deadline**: Before development start
   - **Impact**: Affects database schema and import processes

2. **Bulk Query Limits** (Bot & UX)
   - **Owner**: Product Owner + Tech Lead
   - **Deadline**: Before bot implementation
   - **Impact**: Affects user flow and validation logic

3. **AI Implementation** (AI Search)
   - **Owner**: Tech Lead
   - **Deadline**: Before search implementation
   - **Impact**: Affects architecture and dependencies

4. **SPA Framework** (Admin Panel)
   - **Owner**: Tech Lead
   - **Deadline**: Before admin panel development
   - **Impact**: Affects development stack and timeline

### Medium Priority Decisions (During Development)

5. **Order Reference Numbers** (Orders & Leads)
   - **Owner**: Product Owner
   - **Deadline**: Before order implementation
   - **Impact**: Affects user communication and tracking

6. **Price Update Process** (Data & Sources)
   - **Owner**: Product Owner
   - **Deadline**: Before price management implementation
   - **Impact**: Affects operational workflows

### Low Priority Decisions (Post-MVP)

7. **Multi-language Support** (Bot & UX)
   - **Owner**: Product Owner
   - **Deadline**: Future enhancement
   - **Impact**: Expansion feature

8. **Advanced AI Features** (AI Search)
   - **Owner**: Tech Lead
   - **Deadline**: Post-MVP optimization
   - **Impact**: Performance and accuracy improvements

## 5. Decision Log Template

For each resolved question, maintain a decision log entry:

```markdown
### [Question Title]
- **Date Resolved**: YYYY-MM-DD
- **Decision Made**: [Brief description of decision]
- **Rationale**: [Why this decision was made]
- **Impact**: [How this affects the project]
- **Documentation Updated**: [Which docs need updating]
```

## 6. Next Steps

### Immediate Actions Required

1. **Schedule Decision Meetings**
   - Product Owner: Data source and UX decisions
   - Tech Lead: Technical architecture decisions
   - Stakeholder alignment on business requirements

2. **Create Decision Timeline**
   - High priority decisions: Week 1
   - Medium priority decisions: Week 2-3
   - Low priority decisions: Post-MVP planning

3. **Prepare Decision Materials**
   - Cost-benefit analysis for each option
   - Technical feasibility assessments
   - User impact evaluations

### Documentation Updates

Once decisions are made, update the following documents:
- `/docs/brief.md`: Update scope and constraints
- `/docs/architecture.md`: Update technical specifications
- `/docs/data-model.md`: Update schema and validation rules
- `/docs/user-flows.md`: Update flow details and edge cases

### Development Readiness Checklist

- [ ] All high-priority questions resolved
- [ ] Decision log completed
- [ ] Documentation updated
- [ ] Stakeholder approval obtained
- [ ] Development timeline confirmed
- [ ] Resource allocation finalized

---

*Document Version: 1.0*  
*Last Updated: Initial Creation*  
*Status: Active - Awaiting Decisions*
