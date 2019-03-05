async function API(body, url) {
  const requestParams = {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  }

  const response = await fetch(url, requestParams)
  if (response.ok) return await response.json()
  const err = await response.json()
  throw new Error(err.error)
}

function getNewMonitorFormData() {
  return {
    name: document.getElementById("name").value,
    enabled: document.getElementById("monitorEnabled").checked,
    base_url: document.getElementById("base_url").value,
    login_path: document.getElementById("login_path").value,
    monitor_path: document.getElementById("monitor_path").value,
    username: document.getElementById("username").value,
    password: document.getElementById("password").value
  }
}

function testMonitor() {
  const url = '/api/test'
  const body = getNewMonitorFormData()
  API(body, url).then(response => {
    const testSuccessIcon = document.getElementById("test_success")
    const testErrorIcon = document.getElementById("test_error")

    if (response.success) {
      console.log('Monitoring test successful')
      testErrorIcon.setAttribute("hidden", true)
      testSuccessIcon.removeAttribute("hidden")
    } else {
      console.log('Monitoring test failed')
      testErrorIcon.removeAttribute("hidden")
      testSuccessIcon.setAttribute("hidden", true)
    }
  }).catch(alert)
}

function addNewMonitor() {
  const url = '/api/monitors'
  const body = getNewMonitorFormData()
  API(body, url).then(response => redirectToIndex()).catch(alert)
}

async function deleteMonitor(monitorName) {
  const url = `/api/monitors/${monitorName}`
  const requestParams = {
    method: 'DELETE'
  }
  const response = await fetch(url, requestParams)
  if (response.ok) {
    document.location.reload()
    console.log('Deleted')
  } else {
    const err = await response.json()
    alert(err)
  }
}

function redirectToIndex() {
  document.location = '/'
}
