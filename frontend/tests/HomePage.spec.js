import { mount } from '@vue/test-utils'
import HomePage from '@/pages/HomePage.vue'

// Command to use to install jest:
// npm install --save-dev jest @vue/test-utils vue-jest@next babel-jest @babel/preset-env


describe('Homepage.vue', () => {
  const wrapper = mount(HomePage)
  const importButton = wrapper.findAll('button').filter(b => b.text().match('Import CSV')).at(0)
  const algoButton = wrapper.findAll('button').filter(b => b.text().match('RUN ALGORITHM')).at(0)

  it('renders the UNO logo image', () => {
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toContain('uno-logo.png')
  })

  it('has an import button', () => {
    expect(importButton.exists()).toBe(true)
  })
  
  it('has an algorithm button', () => {
    expect(algoButton.exists()).toBe(true)
  })
})