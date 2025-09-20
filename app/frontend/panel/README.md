# Admin Panel - Chinese Auto Parts Price Bot

This is the admin panel for managing the Chinese Auto Parts Price Bot system.

## Technology Stack

- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS
- **HTTP Client**: Axios
- **State Management**: Pinia (when needed)

## Setup Instructions

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd app/frontend/panel

# Install dependencies
npm install

# Start development server
npm run dev
```

### Build for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The admin panel will integrate with the FastAPI backend through the following endpoints:

### Health Check
- `GET /health` - Check API health status

### Settings Management
- `GET /api/v1/admin/settings` - Get system settings
- `PUT /api/v1/admin/settings` - Update system settings

### Parts Management
- `GET /api/v1/parts` - List parts
- `POST /api/v1/parts` - Create part
- `PUT /api/v1/parts/{id}` - Update part
- `DELETE /api/v1/parts/{id}` - Delete part

### Orders Management
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}` - Update order status

### Leads Management
- `GET /api/v1/leads` - List leads/customers
- `GET /api/v1/leads/{id}` - Get lead details
- `PUT /api/v1/leads/{id}` - Update lead information

## Development Notes

This is a skeleton structure. The actual Vue.js application will be implemented in the next development phase with:

- Authentication system
- Dashboard with role-based access
- Parts management interface
- Orders workflow management
- Settings configuration panel
- Real-time updates and notifications

## Environment Configuration

The frontend will use environment variables for API configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_APP_TITLE=Chinese Auto Parts Admin Panel
```

## Deployment

The built application will be served by the FastAPI backend or a separate web server in production.
