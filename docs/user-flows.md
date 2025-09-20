# Chinese Auto Parts Price Bot - User Flows Documentation

## 1. Purpose & Scope

User flows are critical for ensuring a smooth and intuitive experience across both the Telegram bot interface and admin panel. These flows define the exact user journey from initial part search through order completion, ensuring consistent Persian language support for end users while providing efficient English-based administrative tools. Proper flow design prevents user confusion, reduces support requests, and ensures data quality through structured confirmation steps.

## 2. Telegram Bot Flows

### 2.1 Start & Help Flow

**Step-by-Step Flow:**
1. User opens bot and sends `/start`
2. Bot responds with welcome message in Persian
3. Bot provides example queries and available commands
4. User can send `/help` anytime for assistance
5. Bot explains available features and usage examples

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    
    U->>TG: /start
    TG->>BOT: Command received
    BOT->>TG: "خوش آمدید! برای جستجوی قطعات خودرو چینی از برندهای چری، جک، بریلیانس و غیره استفاده کنید."
    TG->>U: Welcome message
    
    BOT->>TG: "مثال: لنت ترمز جلو تیگو ۸ یا فیلتر روغن X22"
    TG->>U: Example queries
    
    BOT->>TG: "برای جستجوی چندین قطعه، هر قطعه را در یک خط جداگانه بنویسید"
    TG->>U: Bulk search instructions
    
    Note over U,BOT: User can now proceed with part queries
```

### 2.2 Single Part Query Flow

**Step-by-Step Flow:**
1. User sends part query (e.g., "لنت جلو تیگو ۸")
2. Bot processes query using current search method (AI or basic)
3. Bot finds best matching part(s)
4. Bot asks for confirmation with specific part details
5. If user confirms → proceed to Contact Capture
6. If user denies → ask for refined search
7. If no matches found → suggest alternatives

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    
    U->>TG: "لنت جلو تیگو ۸"
    TG->>BOT: Message received
    BOT->>API: POST /search/parts {"query": "لنت جلو تیگو ۸"}
    
    API->>DB: SELECT * FROM parts WHERE...
    API->>API: Apply search logic (AI/basic)
    DB-->>API: Matching parts
    API-->>BOT: Best match with details
    
    BOT->>TG: "آیا شما به دنبال لنت چراغ جلوی تیگو ۸ هستید؟"
    TG->>U: Confirmation question
    
    alt User Confirms (بله)
        U->>TG: "بله"
        TG->>BOT: Confirmation received
        Note over BOT: Proceed to Contact Capture Flow
    else User Denies (خیر)
        U->>TG: "خیر"
        TG->>BOT: Denial received
        BOT->>TG: "لطفاً جستجوی دقیق‌تری انجام دهید"
        TG->>U: Refined search prompt
    else No Matches Found
        BOT->>TG: "قطعه مورد نظر یافت نشد. لطفاً نام برند یا مدل را مشخص کنید"
        TG->>U: Alternative search suggestion
    end
```

### 2.3 Bulk Part Query Flow

**Step-by-Step Flow:**
1. User sends multi-line part list (5-20 items)
2. Bot validates bulk limit
3. Bot processes each line individually
4. Bot creates summary of found/not found items
5. Bot asks for overall confirmation
6. If confirmed → proceed to Contact Capture
7. If denied → ask user to refine list

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    
    U->>TG: Multi-line part list (5-20 items)
    TG->>BOT: Bulk message received
    BOT->>BOT: Count lines and validate limit
    
    alt Exceeds Limit
        BOT->>TG: "تعداد قطعات بیش از حد مجاز است. لطفاً لیست را کوتاه‌تر کنید"
        TG->>U: Limit exceeded warning
    else Within Limit
        BOT->>API: POST /search/bulk {"queries": [...]}
        
        loop For each part in list
            API->>DB: Search part
            DB-->>API: Match result
        end
        
        API-->>BOT: Summary of matches/misses
        BOT->>TG: "یافت شد: 8 قطعه\nیافت نشد: 2 قطعه\n\nآیا می‌خواهید با این موارد ادامه دهید؟"
        TG->>U: Bulk confirmation summary
        
        alt User Confirms (بله)
            U->>TG: "بله"
            TG->>BOT: Confirmation received
            Note over BOT: Proceed to Contact Capture Flow
        else User Denies (خیر)
            U->>TG: "خیر"
            TG->>BOT: Denial received
            BOT->>TG: "لطفاً لیست را اصلاح کنید"
            TG->>U: Refinement request
        end
    end
```

### 2.4 Contact Capture Flow

**Step-by-Step Flow:**
1. Bot checks if lead exists for `telegram_user_id`
2. If no lead exists → request contact via `request_contact`
3. User shares phone number and name
4. Bot optionally asks for city/location
5. Bot stores/updates lead information
6. If lead already exists → skip contact capture
7. Proceed to Order Creation

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    
    Note over BOT: After part confirmation
    BOT->>API: GET /leads/{telegram_user_id}
    API->>DB: SELECT * FROM leads WHERE telegram_user_id = ?
    DB-->>API: Lead data
    
    alt Lead Exists
        API-->>BOT: Existing lead data
        BOT->>BOT: Skip contact capture
        Note over BOT: Proceed directly to Order Creation
    else No Lead Found
        API-->>BOT: No lead found
        BOT->>TG: "برای تکمیل سفارش، لطفاً شماره تماس خود را ارسال کنید"
        TG->>U: Contact request message
        
        BOT->>TG: [InlineKeyboard with request_contact button]
        TG->>U: Contact sharing button
        
        U->>TG: Shares contact (phone + name)
        TG->>BOT: Contact data received
        
        BOT->>TG: "شهر محل سکونت خود را وارد کنید (اختیاری)"
        TG->>U: Optional city request
        
        U->>TG: "تهران" (optional)
        TG->>BOT: City information
        
        BOT->>API: POST /leads {"telegram_user_id": "...", "phone": "...", "name": "...", "city": "..."}
        API->>DB: INSERT/UPDATE leads
        DB-->>API: Lead created/updated
        API-->>BOT: Success confirmation
        
        Note over BOT: Proceed to Order Creation
    end
```

### 2.5 Order Creation Flow

**Step-by-Step Flow:**
1. Bot creates new order record
2. Bot creates order_items for each confirmed part
3. Bot links order to lead
4. Bot sends confirmation message
5. Bot provides order reference number
6. Admin notification (optional)

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    participant ADMIN as Admin
    
    Note over BOT: After contact capture
    BOT->>API: POST /orders {"lead_id": "...", "items": [...]}
    
    API->>DB: BEGIN TRANSACTION
    API->>DB: INSERT INTO orders (lead_id, status, notes)
    DB-->>API: Order created with ID
    
    loop For each confirmed part
        API->>DB: INSERT INTO order_items (order_id, line_no, query_text, matched_part_id, qty)
    end
    
    API->>DB: COMMIT TRANSACTION
    DB-->>API: Transaction successful
    API-->>BOT: Order created with reference
    
    BOT->>TG: "سفارش شما با موفقیت ثبت شد.\nشماره سفارش: #ORD-12345\nتیم ما به زودی با شما تماس خواهد گرفت."
    TG->>U: Order confirmation
    
    Note over ADMIN: Admin receives notification of new order
```

### 2.6 Admin Commands Flow

**Step-by-Step Flow:**
1. Admin sends `/ai on` or `/ai off`
2. Bot validates admin permissions
3. Bot updates settings in database
4. Bot confirms setting change
5. Setting takes effect immediately

```mermaid
sequenceDiagram
    participant A as Admin
    participant TG as Telegram
    participant BOT as Bot
    participant API as FastAPI
    participant DB as Database
    
    A->>TG: /ai on
    TG->>BOT: Command received
    BOT->>API: GET /users/admin/{telegram_user_id}
    API->>DB: Check admin permissions
    DB-->>API: User role data
    
    alt Is Admin
        API-->>BOT: Admin confirmed
        BOT->>API: PUT /settings/AI_ENABLED {"value": "true"}
        API->>DB: UPDATE settings SET value = 'true' WHERE key = 'AI_ENABLED'
        DB-->>API: Setting updated
        API-->>BOT: Success confirmation
        
        BOT->>TG: "جستجوی هوش مصنوعی فعال شد"
        TG->>A: Confirmation message
    else Not Admin
        API-->>BOT: Access denied
        BOT->>TG: "شما مجوز لازم برای این عملیات را ندارید"
        TG->>A: Error message
    end
```

## 3. Admin Panel Flows

### 3.1 Login & Role Check Flow

**Step-by-Step Flow:**
1. Admin/Operator/Manager accesses admin panel
2. User enters username and password
3. System validates credentials
4. System checks user role and permissions
5. User redirected to appropriate dashboard
6. Session established with role-based access

```mermaid
sequenceDiagram
    participant U as User
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    U->>PANEL: Access admin panel URL
    PANEL->>U: Login form displayed
    
    U->>PANEL: Enter username/password
    PANEL->>API: POST /auth/login {"username": "...", "password": "..."}
    
    API->>DB: SELECT * FROM users WHERE username = ? AND is_active = true
    DB-->>API: User data
    
    alt Valid Credentials
        API->>API: Verify password hash
        API->>DB: UPDATE users SET last_login = NOW() WHERE id = ?
        API-->>PANEL: JWT token with role claims
        
        PANEL->>PANEL: Store token and redirect
        
        alt Admin Role
            PANEL->>U: Full admin dashboard
        else Operator Role
            PANEL->>U: Operator dashboard (limited access)
        else Manager Role
            PANEL->>U: Manager dashboard (reports + oversight)
        end
    else Invalid Credentials
        API-->>PANEL: Authentication failed
        PANEL->>U: Error message - try again
    end
```

### 3.2 Parts Management Flow

**Step-by-Step Flow:**
1. Admin accesses parts management section
2. Admin can view, search, and filter parts
3. Admin can add new parts manually
4. Admin can import parts via Excel upload
5. Admin can edit existing parts
6. Admin can manage synonyms for better search

```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    A->>PANEL: Navigate to Parts Management
    PANEL->>API: GET /parts?page=1&limit=50&search=...
    API->>DB: SELECT * FROM parts WHERE ... LIMIT 50
    DB-->>API: Parts data
    API-->>PANEL: Paginated parts list
    PANEL->>A: Display parts table
    
    alt Add New Part
        A->>PANEL: Click "Add Part"
        PANEL->>A: Part form displayed
        A->>PANEL: Fill part details (name, OEM code, vehicle, etc.)
        PANEL->>API: POST /parts {"part_name": "...", "oem_code": "..."}
        API->>DB: INSERT INTO parts (...)
        DB-->>API: Part created
        API-->>PANEL: Success response
        PANEL->>A: Part added confirmation
    else Import Excel
        A->>PANEL: Click "Import Excel"
        PANEL->>A: File upload dialog
        A->>PANEL: Upload parts_template.xlsx
        PANEL->>API: POST /import/excel (file upload)
        API->>API: Parse and validate Excel data
        API->>DB: Bulk INSERT parts
        DB-->>API: Import results
        API-->>PANEL: Import summary (success/errors)
        PANEL->>A: Import results displayed
    else Edit Part
        A->>PANEL: Click edit on existing part
        PANEL->>API: GET /parts/{id}
        API->>DB: SELECT * FROM parts WHERE id = ?
        DB-->>API: Part details
        API-->>PANEL: Part data
        PANEL->>A: Edit form with current data
        A->>PANEL: Modify part details
        PANEL->>API: PUT /parts/{id} {...}
        API->>DB: UPDATE parts SET ... WHERE id = ?
        DB-->>API: Update successful
        API-->>PANEL: Success response
        PANEL->>A: Part updated confirmation
    end
```

### 3.3 Prices Management Flow

**Step-by-Step Flow:**
1. Admin accesses prices section
2. Admin can view prices by part
3. Admin can add/update prices manually
4. Admin can import prices via Excel
5. Admin can view price history
6. Admin can assign sellers to parts

```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    A->>PANEL: Navigate to Prices Management
    PANEL->>API: GET /prices?part_id=...&page=1
    API->>DB: SELECT * FROM prices WHERE part_id = ? ORDER BY created_at DESC
    DB-->>API: Prices data
    API-->>PANEL: Prices list
    PANEL->>A: Display prices table
    
    alt Add New Price
        A->>PANEL: Click "Add Price"
        PANEL->>A: Price form displayed
        A->>PANEL: Fill price details (seller, price, currency, validity)
        PANEL->>API: POST /prices {"part_id": "...", "seller_name": "...", "price": "..."}
        API->>DB: INSERT INTO prices (...)
        DB-->>API: Price created
        API-->>PANEL: Success response
        PANEL->>A: Price added confirmation
    else Import Price Data
        A->>PANEL: Click "Import Prices"
        PANEL->>A: Excel upload dialog
        A->>PANEL: Upload price data file
        PANEL->>API: POST /import/prices (file upload)
        API->>API: Parse price data and validate
        API->>DB: Bulk INSERT/UPDATE prices
        DB-->>API: Import results
        API-->>PANEL: Import summary
        PANEL->>A: Price import results
    else View Price History
        A->>PANEL: Select part to view history
        PANEL->>API: GET /prices/history?part_id=...
        API->>DB: SELECT * FROM prices WHERE part_id = ? ORDER BY created_at
        DB-->>API: Historical prices
        API-->>PANEL: Price history data
        PANEL->>A: Price trend chart/table
    end
```

### 3.4 Orders Workflow

**Step-by-Step Flow:**
1. Admin views incoming orders (status=new)
2. Operator updates order status to in_progress
3. Operator contacts customer and provides quote
4. Operator updates status to quoted
5. Manager reviews and approves final quotes
6. Order status updated to won/lost

```mermaid
sequenceDiagram
    participant OP as Operator
    participant MGR as Manager
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    OP->>PANEL: Navigate to Orders
    PANEL->>API: GET /orders?status=new&page=1
    API->>DB: SELECT * FROM orders WHERE status = 'new' ORDER BY created_at
    DB-->>API: New orders
    API-->>PANEL: Orders list
    PANEL->>OP: Display new orders
    
    OP->>PANEL: Select order to process
    PANEL->>API: GET /orders/{id}
    API->>DB: SELECT * FROM orders o JOIN order_items oi ON o.id = oi.order_id WHERE o.id = ?
    DB-->>API: Order details with items
    API-->>PANEL: Complete order data
    PANEL->>OP: Order details with customer info
    
    OP->>PANEL: Update status to "in_progress"
    PANEL->>API: PUT /orders/{id} {"status": "in_progress"}
    API->>DB: UPDATE orders SET status = 'in_progress' WHERE id = ?
    DB-->>API: Status updated
    API-->>PANEL: Success response
    
    Note over OP: Operator contacts customer
    
    OP->>PANEL: Add quote and update to "quoted"
    PANEL->>API: PUT /orders/{id} {"status": "quoted", "notes": "Quote provided: ..."}
    API->>DB: UPDATE orders SET status = 'quoted', notes = '...' WHERE id = ?
    
    MGR->>PANEL: Review quoted orders
    PANEL->>API: GET /orders?status=quoted
    API->>DB: SELECT * FROM orders WHERE status = 'quoted'
    DB-->>API: Quoted orders
    API-->>PANEL: Quoted orders list
    PANEL->>MGR: Display orders awaiting approval
    
    MGR->>PANEL: Approve order (won) or reject (lost)
    PANEL->>API: PUT /orders/{id} {"status": "won"}
    API->>DB: UPDATE orders SET status = 'won' WHERE id = ?
    DB-->>API: Final status updated
    API-->>PANEL: Success response
    PANEL->>MGR: Order status updated
```

### 3.5 Leads Management Flow

**Step-by-Step Flow:**
1. Admin views captured customer leads
2. Admin can search/filter leads by various criteria
3. Admin can edit/update lead information
4. Admin can view order history per lead
5. Admin can add notes to leads
6. Admin can manage lead status

```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    A->>PANEL: Navigate to Leads Management
    PANEL->>API: GET /leads?page=1&search=...
    API->>DB: SELECT * FROM leads WHERE ... ORDER BY created_at DESC
    DB-->>API: Leads data
    API-->>PANEL: Paginated leads list
    PANEL->>A: Display leads table
    
    A->>PANEL: Select lead to view details
    PANEL->>API: GET /leads/{id}
    API->>DB: SELECT * FROM leads WHERE id = ?
    DB-->>API: Lead details
    API-->>PANEL: Lead information
    PANEL->>A: Lead details with contact info
    
    alt Edit Lead Information
        A->>PANEL: Click "Edit Lead"
        PANEL->>A: Edit form with current data
        A->>PANEL: Modify lead details (phone, city, notes)
        PANEL->>API: PUT /leads/{id} {"phone_e164": "...", "city": "...", "notes": "..."}
        API->>DB: UPDATE leads SET ... WHERE id = ?
        DB-->>API: Update successful
        API-->>PANEL: Success response
        PANEL->>A: Lead updated confirmation
    else View Order History
        A->>PANEL: Click "View Orders"
        PANEL->>API: GET /orders?lead_id={id}
        API->>DB: SELECT * FROM orders WHERE lead_id = ? ORDER BY created_at
        DB-->>API: Order history
        API-->>PANEL: Orders for this lead
        PANEL->>A: Display order history table
    else Add Notes
        A->>PANEL: Click "Add Note"
        PANEL->>A: Notes text area
        A->>PANEL: Enter additional notes
        PANEL->>API: PUT /leads/{id} {"notes": "Previous notes + new note"}
        API->>DB: UPDATE leads SET notes = ... WHERE id = ?
        DB-->>API: Notes updated
        API-->>PANEL: Success response
        PANEL->>A: Notes added confirmation
    end
```

### 3.6 Settings Management Flow

**Step-by-Step Flow:**
1. Admin accesses settings panel
2. Admin can toggle AI search on/off
3. Admin can adjust bulk query limits
4. Admin can configure maintenance mode
5. Admin can manage other system settings
6. Changes take effect immediately

```mermaid
sequenceDiagram
    participant A as Admin
    participant PANEL as Admin Panel
    participant API as FastAPI
    participant DB as Database
    
    A->>PANEL: Navigate to Settings
    PANEL->>API: GET /settings
    API->>DB: SELECT * FROM settings
    DB-->>API: Current settings
    API-->>PANEL: Settings data
    PANEL->>A: Display settings form
    
    alt Toggle AI Search
        A->>PANEL: Toggle AI_ENABLED switch
        PANEL->>API: PUT /settings/AI_ENABLED {"value": "false"}
        API->>DB: UPDATE settings SET value = 'false', updated_at = NOW() WHERE key = 'AI_ENABLED'
        DB-->>API: Setting updated
        API-->>PANEL: Success response
        PANEL->>A: "AI Search disabled"
    else Adjust Bulk Limit
        A->>PANEL: Change BULK_LIMIT value
        PANEL->>API: PUT /settings/BULK_LIMIT {"value": "15"}
        API->>DB: UPDATE settings SET value = '15', updated_at = NOW() WHERE key = 'BULK_LIMIT'
        DB-->>API: Setting updated
        API-->>PANEL: Success response
        PANEL->>A: "Bulk limit updated to 15"
    else Enable Maintenance Mode
        A->>PANEL: Toggle MAINTENANCE_MODE
        PANEL->>API: PUT /settings/MAINTENANCE_MODE {"value": "true"}
        API->>DB: UPDATE settings SET value = 'true' WHERE key = 'MAINTENANCE_MODE'
        DB-->>API: Setting updated
        API-->>PANEL: Success response
        PANEL->>A: "Maintenance mode enabled"
        
        Note over API,DB: Bot will show maintenance message to users
    end
```

## 4. Edge Cases & Exceptions

### 4.1 User Denies Confirmation
- **Scenario**: User responds "خیر" to part confirmation
- **Response**: Bot asks for refined search terms
- **Flow**: Return to query step with guidance

### 4.2 Bulk Query Limit Exceeded
- **Scenario**: User sends >20 parts in bulk query
- **Response**: Bot shows warning and asks to shorten list
- **Limit**: Configurable via settings (default 10-20)

### 4.3 Duplicate Phone Number
- **Scenario**: User shares phone number already in system
- **Response**: Bot recognizes existing lead, skips contact capture
- **Action**: Link new order to existing lead record

### 4.4 Admin Permission Denied
- **Scenario**: Non-admin user tries to use admin commands
- **Response**: Bot shows error message
- **Security**: Only telegram_user_ids in admin list can use commands

### 4.5 No Search Results Found
- **Scenario**: Part query returns no matches
- **Response**: Bot suggests alternatives or asks for more specific terms
- **Fallback**: Suggest checking spelling or brand name

### 4.6 Database Connection Issues
- **Scenario**: Backend cannot connect to database
- **Response**: Bot shows maintenance message
- **Recovery**: Automatic retry with graceful degradation

### 4.7 AI Service Unavailable
- **Scenario**: AI search fails but basic search works
- **Response**: Automatically fall back to basic search
- **Transparency**: User not notified of fallback

## 5. UX Notes

### 5.1 Language Support
- **End Users**: All bot interactions in Persian
- **Admin Panel**: English interface with Persian data display
- **Error Messages**: User-friendly Persian messages
- **Confirmation Questions**: Clear, specific Persian confirmations

### 5.2 Response Design
- **Concise Messages**: Short, clear responses
- **Confirmation Required**: Always confirm before data capture
- **Progress Indication**: Show processing status for bulk queries
- **Error Handling**: Helpful error messages with suggestions

### 5.3 Accessibility
- **Keyboard Support**: Full keyboard navigation in admin panel
- **Mobile Friendly**: Bot optimized for mobile Telegram interface
- **Clear Navigation**: Intuitive flow between steps

## 6. Next Steps

### 6.1 Flow Validation
- **User Testing**: Validate flows with target users (mechanics, sellers, retail customers)
- **Edge Case Testing**: Comprehensive testing of all exception scenarios
- **Performance Testing**: Ensure flows work smoothly under load

### 6.2 UI/UX Refinement
- **Bot Interface**: Finalize Persian message templates and button layouts
- **Admin Panel**: Complete UI design for all management screens
- **Responsive Design**: Ensure admin panel works on all devices

### 6.3 Integration Points
- **Telegram API**: Finalize webhook configuration and error handling
- **Database**: Complete schema implementation with all constraints
- **Search Logic**: Implement AI/basic search switching mechanism

### 6.4 Documentation Completion
- **Proceed to**: `/docs/open-questions.md` for unresolved items
- **Finalize**: All remaining open questions from project brief
- **Prepare**: Development task breakdown and implementation plan

---

*Document Version: 1.0*  
*Last Updated: Initial Creation*  
*Status: Draft - Awaiting Review*
