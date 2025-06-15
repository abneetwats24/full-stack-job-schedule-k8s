import { createApp, ref } from 'vue'
import axios from 'axios'

const App = {
  setup() {
    const payload = ref('{}')
    const callbackUrl = window.location.origin + '/webhook-demo' // placeholder
    const correlationId = ref('')
    const result = ref('')

    const submit = async () => {
      const res = await axios.post('/api/process', {
        callback_url: callbackUrl,
        payload: JSON.parse(payload.value || '{}'),
      })
      correlationId.value = res.data.correlation_id
    }

    return { payload, correlationId, result, submit }
  },
  template: `
    <h1>Async Processor Demo</h1>
    <textarea v-model="payload" rows="5" cols="40"></textarea><br />
    <button @click="submit">Submit Job</button>
    <p v-if="correlationId">Correlation ID: {{ correlationId }}</p>
  `,
}

createApp(App).mount('#app')
