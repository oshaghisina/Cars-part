import CrossReferences from '../components/pdp/CrossReferences.vue'

export default {
  title: 'PDP/CrossReferences',
  component: CrossReferences,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    partId: {
      control: { type: 'text' },
      description: 'Part ID for cross-references'
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Loading state'
    }
  }
}

export const Default = {
  args: {
    partId: '1',
    loading: false
  }
}

export const Loading = {
  args: {
    partId: '1',
    loading: true
  }
}

export const WithData = {
  args: {
    partId: '1',
    loading: false,
    oemReferences: [
      {
        id: 1,
        oem_number: '12345-67890',
        brand: 'Toyota',
        description: 'Original Toyota part',
        price: 65.99,
        stock: 'in_stock'
      },
      {
        id: 2,
        oem_number: '98765-43210',
        brand: 'Honda',
        description: 'Honda equivalent',
        price: 58.99,
        stock: 'low_stock'
      }
    ],
    alternatives: [
      {
        id: 3,
        name: 'Alternative Brake Pad',
        brand: 'Brembo',
        price: 42.99,
        stock: 'in_stock',
        rating: 4.5,
        compatibility: 95
      }
    ],
    supersessions: [
      {
        id: 4,
        name: 'Updated Brake Pad Set',
        supersedes: 'BP-FRONT-001',
        improvements: 'Better heat resistance',
        price: 48.99,
        stock: 'in_stock'
      }
    ]
  }
}
