import PartDetail from '../views/PartDetail.vue'

export default {
  title: 'Pages/PartDetail',
  component: PartDetail,
  parameters: {
    layout: 'fullscreen',
  },
  argTypes: {
    partId: {
      control: { type: 'text' },
      description: 'The ID of the part to display'
    }
  }
}

export const Default = {
  args: {
    partId: '1'
  }
}

export const WithTestProduct = {
  args: {
    partId: '14'
  }
}

export const Loading = {
  args: {
    partId: '999'
  }
}
