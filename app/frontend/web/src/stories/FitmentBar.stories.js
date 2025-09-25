import FitmentBar from '../components/pdp/FitmentBar.vue'

export default {
  title: 'PDP/FitmentBar',
  component: FitmentBar,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    partId: {
      control: { type: 'text' },
      description: 'Part ID for compatibility checking'
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

export const Compatible = {
  args: {
    partId: '1',
    loading: false,
    compatibilityStatus: {
      isCompatible: true,
      message: 'This part is compatible with your vehicle',
      vehicleInfo: {
        make: 'Toyota',
        model: 'Camry',
        year: 2020,
        trim: 'LE'
      }
    }
  }
}

export const Incompatible = {
  args: {
    partId: '1',
    loading: false,
    compatibilityStatus: {
      isCompatible: false,
      message: 'This part is not compatible with your vehicle',
      vehicleInfo: {
        make: 'Honda',
        model: 'Civic',
        year: 2019,
        trim: 'LX'
      }
    }
  }
}
