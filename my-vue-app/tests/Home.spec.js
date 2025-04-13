import { mount } from '@vue/test-utils'
import HomePage from '@/pages/HomePage.vue'

// Command to use to install jest:
// npm install --save-dev jest @vue/test-utils vue-jest@next babel-jest @babel/preset-env


describe('Homepage.vue', () => {
    it('renders the UNO logo image', () => {
      const wrapper = mount(HomePage)
      const img = wrapper.find('img')
      expect(img.exists()).toBe(true)
      expect(img.attributes('src')).toContain('uno-logo.png')
    })
  
    it('has an import button', () => {
      const wrapper = mount(HomePage)
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text().toLowerCase()).toContain('import csv')
    })
  })