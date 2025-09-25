import BuyBox from '../components/pdp/BuyBox.vue'

export default {
  title: 'PDP/BuyBox',
  component: BuyBox,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    part: {
      control: { type: 'object' },
      description: 'Part data object'
    },
    userLocation: {
      control: { type: 'text' },
      description: 'User location for delivery estimation'
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Loading state'
    }
  }
}

const mockPart = {
  id: 1,
  name: 'Brake Pad Set - Front',
  sku: 'BP-FRONT-001',
  brand: 'Bosch',
  price: {
    retail: 45.99,
    pro: 38.99,
    currency: 'USD'
  },
  stock: {
    quantity: 15,
    status: 'in_stock',
    next_stock_date: null
  },
  quantity_breaks: [
    { min_quantity: 1, max_quantity: 4, discount_percent: 0 },
    { min_quantity: 5, max_quantity: 9, discount_percent: 5 },
    { min_quantity: 10, max_quantity: 24, discount_percent: 10 },
    { min_quantity: 25, max_quantity: null, discount_percent: 15 }
  ],
  moq: 1,
  delivery_estimation: {
    standard: '3-5 business days',
    express: '1-2 business days'
  }
}

export const Default = {
  args: {
    part: mockPart,
    userLocation: 'Tehran',
    loading: false
  }
}

export const Loading = {
  args: {
    part: null,
    userLocation: 'Tehran',
    loading: true
  }
}

export const LowStock = {
  args: {
    part: {
      ...mockPart,
      stock: {
        quantity: 2,
        status: 'low_stock',
        next_stock_date: '2024-02-15'
      }
    },
    userLocation: 'Tehran',
    loading: false
  }
}

export const OutOfStock = {
  args: {
    part: {
      ...mockPart,
      stock: {
        quantity: 0,
        status: 'out_of_stock',
        next_stock_date: '2024-02-15'
      }
    },
    userLocation: 'Tehran',
    loading: false
  }
}

export const ProUser = {
  args: {
    part: {
      ...mockPart,
      user_type: 'pro'
    },
    userLocation: 'Tehran',
    loading: false
  }
}
