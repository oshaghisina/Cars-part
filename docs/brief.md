# Chinese Auto Parts Price Bot - Project Brief

## Problem Statement

The market for Chinese car parts (MVM, Chery, JAC, Brilliance, etc.) is fragmented. Buyers often need to make multiple calls or search across different sites to find accurate prices, leading to inefficient purchasing processes and time-consuming price discovery.

## Solution Goals

Build a Telegram Price Bot with FastAPI backend and central database that:
- Provides instant part recognition and confirmation in Persian
- Captures customer information for lead generation and order processing
- Supports both single and bulk part queries
- Offers flexible AI-powered search capabilities with admin toggle
- Provides comprehensive admin management for multiple user roles

## Target Users

### End Users
- **Mechanics**: Professional auto repair specialists
- **Auto Parts Sellers**: Retail and wholesale parts dealers
- **Retail Customers**: Individual car owners seeking parts

### System Users
- **Admin**: Full system access and configuration
- **Operator**: Day-to-day order and customer management
- **Manager**: Oversight and reporting capabilities

## Core MVP Features

### Telegram Bot
- `/start` and help messages in Persian
- Single part query: "Front brake pad X22"
- Bulk query: Multi-line input support
- **Part confirmation flow**: After detecting a part (e.g., "Front brake pad Tiggo 8"), bot asks: "آیا شما به دنبال لنت چراغ جلوی تیگو ۸ هستید؟"
- **No direct price display** - only part confirmation → contact capture
- One-time contact capture via `request_contact`
- Formal order submission workflow

### Backend API (FastAPI)
- Part search with basic/fuzzy/AI toggle capability
- Order management system
- Lead (customer) management
- Excel import/export endpoints
- Multi-user role management and authentication

### Database Schema
- `parts`: part definition (name, OEM/ALT codes, category, vehicle)
- `prices`: multiple prices per part with history & source
- `synonyms`: keywords/aliases for better search
- `leads`: customer info (telegram_user_id, phone, city, etc.)
- `orders`: formal requests
- `order_items`: individual items inside orders
- `settings`: feature flags (e.g., AI_ENABLED)
- `users`: roles for panel access (admin, operator, manager)

### Admin Panel (SPA)
- Parts & prices management
- Orders & customers view
- AI search toggle functionality
- Multi-user role management
- Excel import functionality

## Technical Specifications

### Technology Stack
- **Language**: Python 3.11+
- **Backend Framework**: FastAPI
- **Bot Framework**: aiogram
- **Database**: SQLite (MVP) → Postgres later
- **Frontend**: SPA (framework TBD)
- **Infrastructure**: systemd + Caddy (no Docker)

### Localization
- **End-user Interface**: Persian
- **Codebase**: English
- **Documentation**: English

### Scale Requirements
- **Initial Dataset**: 200-500 parts for testing
- **Expected Users**: Scalable architecture for growth

## Out of Scope (Future Features)

- Automated scraping pipelines
- Seller comparison and price history charts
- Online payments and invoicing
- Mobile applications
- Multi-language support beyond Persian

## Constraints

### Technical Constraints
- No Docker deployment (systemd + Caddy preferred)
- SQLite for MVP with planned migration to Postgres
- Persian language support for end users

### Business Constraints
- Focus on Chinese car parts market
- Lead generation and order management priority
- Manual price updates initially

## Open Questions

### Data Management
1. **Initial data source**: How will the initial parts database be populated?
   - Manual Excel entry
   - Automated scraping
   - Sample data generator
   - Combination approach

2. **Bulk query limits**: What's the maximum number of parts per bulk search?
   - 5-10 parts (user-friendly)
   - 20-50 parts (business-focused)
   - Configurable limit with warnings

### Technical Implementation
3. **AI search implementation**: Local embeddings vs external API?
4. **Admin panel framework**: React, Vue, or vanilla JS preference?
5. **Order confirmation flow**: Reference numbers and user notifications?

## Success Metrics

### User Engagement
- Number of active Telegram users
- Query volume (single vs bulk)
- Order conversion rate

### System Performance
- Search response time
- Bot uptime and reliability
- Admin panel usage

## Next Steps

1. Finalize remaining open questions
2. Complete architecture documentation
3. Define detailed data model
4. Map user flows and journeys
5. Begin code scaffolding and development

---

*Document Version: 1.0*  
*Last Updated: Initial Creation*  
*Status: Draft - Awaiting Final Review*
