import ProductManagement from '../components/ProductManagement.vue'

export default {
  title: 'Admin/ProductManagement',
  component: ProductManagement,
  parameters: {
    layout: 'fullscreen',
  }
}

export const Default = {
  args: {}
}

export const WithProducts = {
  args: {
    products: [
      {
        id: 1,
        name: 'Brake Pad Set - Front',
        sku: 'BP-FRONT-001',
        brand: 'Bosch',
        price: 45.99,
        stock: 15,
        status: 'active'
      },
      {
        id: 2,
        name: 'Oil Filter',
        sku: 'OF-001',
        brand: 'Mann',
        price: 12.99,
        stock: 50,
        status: 'active'
      }
    ]
  }
}
