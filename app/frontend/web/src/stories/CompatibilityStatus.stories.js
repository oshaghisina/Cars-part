import CompatibilityStatus from '../components/pdp/shared/CompatibilityStatus.vue'

export default {
  title: 'PDP/Shared/CompatibilityStatus',
  component: CompatibilityStatus,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    status: {
      control: { type: 'object' },
      description: 'Compatibility status object'
    }
  }
}

export const Compatible = {
  args: {
    status: {
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
    status: {
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

export const Checking = {
  args: {
    status: {
      isCompatible: null,
      message: 'Checking compatibility...',
      vehicleInfo: null
    }
  }
}

export const NoVehicle = {
  args: {
    status: {
      isCompatible: null,
      message: 'Please select a vehicle to check compatibility',
      vehicleInfo: null
    }
  }
}
