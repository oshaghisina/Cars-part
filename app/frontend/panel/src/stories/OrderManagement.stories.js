import OrderManagement from "../components/OrderManagement.vue";

export default {
  title: "Admin/OrderManagement",
  component: OrderManagement,
  parameters: {
    layout: "fullscreen",
  },
};

export const Default = {
  args: {},
};

export const WithOrders = {
  args: {
    orders: [
      {
        id: 1,
        order_number: "ORD-001",
        customer_name: "John Doe",
        total: 125.99,
        status: "pending",
        created_at: "2024-01-15T10:30:00Z",
      },
      {
        id: 2,
        order_number: "ORD-002",
        customer_name: "Jane Smith",
        total: 89.5,
        status: "shipped",
        created_at: "2024-01-14T14:20:00Z",
      },
    ],
  },
};
