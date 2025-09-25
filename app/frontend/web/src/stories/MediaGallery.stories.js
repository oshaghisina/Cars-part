import MediaGallery from '../components/pdp/MediaGallery.vue'

export default {
  title: 'PDP/MediaGallery',
  component: MediaGallery,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    images: {
      control: { type: 'object' },
      description: 'Array of product images'
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Loading state'
    }
  }
}

const mockImages = [
  {
    id: 1,
    image_url: 'https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Product+Image+1',
    alt_text: 'Product front view',
    sort_order: 1,
    is_active: true,
    thumbnails: {
      small: 'https://via.placeholder.com/150x150/4F46E5/FFFFFF?text=Thumb+1',
      medium: 'https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Thumb+1',
      large: 'https://via.placeholder.com/600x600/4F46E5/FFFFFF?text=Thumb+1'
    }
  },
  {
    id: 2,
    image_url: 'https://via.placeholder.com/800x600/10B981/FFFFFF?text=Product+Image+2',
    alt_text: 'Product side view',
    sort_order: 2,
    is_active: true,
    thumbnails: {
      small: 'https://via.placeholder.com/150x150/10B981/FFFFFF?text=Thumb+2',
      medium: 'https://via.placeholder.com/300x300/10B981/FFFFFF?text=Thumb+2',
      large: 'https://via.placeholder.com/600x600/10B981/FFFFFF?text=Thumb+2'
    }
  },
  {
    id: 3,
    image_url: 'https://via.placeholder.com/800x600/F59E0B/FFFFFF?text=Product+Image+3',
    alt_text: 'Product back view',
    sort_order: 3,
    is_active: true,
    thumbnails: {
      small: 'https://via.placeholder.com/150x150/F59E0B/FFFFFF?text=Thumb+3',
      medium: 'https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Thumb+3',
      large: 'https://via.placeholder.com/600x600/F59E0B/FFFFFF?text=Thumb+3'
    }
  }
]

export const Default = {
  args: {
    images: mockImages,
    loading: false
  }
}

export const Loading = {
  args: {
    images: [],
    loading: true
  }
}

export const SingleImage = {
  args: {
    images: [mockImages[0]],
    loading: false
  }
}

export const NoImages = {
  args: {
    images: [],
    loading: false
  }
}
