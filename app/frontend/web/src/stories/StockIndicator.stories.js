import StockIndicator from '../components/pdp/shared/StockIndicator.vue'

export default {
  title: 'PDP/Shared/StockIndicator',
  component: StockIndicator,
  parameters: {
    layout: 'padded',
  },
  argTypes: {
    stock: {
      control: { type: 'object' },
      description: 'Stock information object'
    }
  }
}

export const InStock = {
  args: {
    stock: {
      quantity: 15,
      status: 'in_stock',
      next_stock_date: null
    }
  }
}

export const LowStock = {
  args: {
    stock: {
      quantity: 2,
      status: 'low_stock',
      next_stock_date: '2024-02-15'
    }
  }
}

export const OutOfStock = {
  args: {
    stock: {
      quantity: 0,
      status: 'out_of_stock',
      next_stock_date: '2024-02-15'
    }
  }
}

export const PreOrder = {
  args: {
    stock: {
      quantity: 0,
      status: 'pre_order',
      next_stock_date: '2024-03-01'
    }
  }
}
