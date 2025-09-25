import TitleBlock from '../components/pdp/TitleBlock.vue'

export default {
  title: 'PDP/TitleBlock',
  component: TitleBlock,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    part: {
      control: { type: 'object' },
      description: 'Part data object'
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
  category: 'Brake System',
  badges: ['Best Seller', 'OEM Quality'],
  rating: 4.5,
  review_count: 128,
  is_wishlisted: false,
  is_compared: false
}

export const Default = {
  args: {
    part: mockPart,
    loading: false
  }
}

export const Loading = {
  args: {
    part: null,
    loading: true
  }
}

export const WithWishlist = {
  args: {
    part: {
      ...mockPart,
      is_wishlisted: true
    },
    loading: false
  }
}

export const WithComparison = {
  args: {
    part: {
      ...mockPart,
      is_compared: true
    },
    loading: false
  }
}

export const HighRated = {
  args: {
    part: {
      ...mockPart,
      rating: 4.8,
      review_count: 256,
      badges: ['Best Seller', 'OEM Quality', 'Top Rated']
    },
    loading: false
  }
}
