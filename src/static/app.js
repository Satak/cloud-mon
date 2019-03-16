document.addEventListener('DOMContentLoaded', function() {
  let elems1 = document.querySelectorAll('.collapsible');
  let instances1 = M.Collapsible.init(elems1);
  let elems2 = document.querySelectorAll('.sidenav');
  let instances2 = M.Sidenav.init(elems2);
  let elems3 = document.querySelectorAll('select');
  let instances3 = M.FormSelect.init(elems3);
})

google.charts.load('current', {packages: ['corechart', 'line']})
function drawLinechart(name) {
  google.charts.setOnLoadCallback(() => drawBasic(name))
}

// TODO: clean this up or start using Vue
function monitorTypeSelect(value) {
  if (value === 'noAuth') {
    document.getElementById('basicAuth').style.display = 'none'
    document.getElementById('tokenAuth').style.display = 'none'
  } else if (value === 'basicAuth') {
    document.getElementById('basicAuth').style.display = 'block'
    document.getElementById('tokenAuth').style.display = 'none'
  } else if (value === 'tokenAuth') {
    document.getElementById('basicAuth').style.display = 'block'
    document.getElementById('tokenAuth').style.display = 'block'
  }
}

async function API(body, url, method) {
  const requestParams = {
    method: method,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }
  if(body) {
    requestParams['body'] = JSON.stringify(body)
  }

  const response = await fetch(url, requestParams)
  if (response.ok) return await response.json()
  const err = await response.json()
  throw new Error(err.error)
}

function getNewMonitorFormData() {
  let body = {
    monitor_type: document.getElementById("monitor_type").value,
    name: document.getElementById("name").value,
    enabled: document.getElementById("monitorEnabled").checked,
    base_url: document.getElementById("base_url").value,
  }
    const loginPathElement = document.getElementById("login_path")
    const monitorPathElement = document.getElementById("monitor_path")
    const usernameElement = document.getElementById("username")
    const passwordElement = document.getElementById("password")
    // lol
    if (loginPathElement) {
      body['login_path'] = loginPathElement.value
    }
    if (monitorPathElement) {
      body['monitor_path'] = monitorPathElement.value
    }
    if (usernameElement) {
      body['username'] = usernameElement.value
    }
    if (passwordElement) {
      body['password'] = passwordElement.value
    }

  return parseBody(body)
}

function testMonitor() {
  const url = '/api/test'
  const body = getNewMonitorFormData()
  const method = 'POST'
  API(body, url, method).then(response => {
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

function parseBody(body) {
  if (body['monitor_type'] === 'noAuth') {
    delete body['username']
    delete body['password']
    delete body['login_path']
    delete body['monitor_path']
  } else if (body['monitor_type'] === 'basicAuth') {
    delete body['login_path']
    delete body['monitor_path']
  }
  return body
}

function addNewMonitor() {
  const method = 'POST'
  const url = '/api/monitors'
  const body = getNewMonitorFormData()
  API(body, url, method).then(_ => redirectToHome()).catch(alert)
}

function modifyMonitor(name) {
  const method = 'PUT'
  const url = `/api/monitors/${name}`
  const body = getNewMonitorFormData()
  API(body, url, method).then(_ => redirectToHome()).catch(alert)
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

function redirectToHome() {
  document.location = '/home'
}

function redirectToIndex() {
  document.location = '/'
}

function invokeMonitor() {
  const method = 'PUT'
  const url = '/api/ui-invoke-monitor'
  const body = {}
  API(body, url, method).then(_ => redirectToHome()).catch(alert)
}

function drawBasic(name) {
  const url = `/api/monitor-data/${name}`
  const data = new google.visualization.DataTable()
  const options = {
    hAxis: {
      title: 'Datetime'
    },
    vAxis: {
      title: 'Milliseconds'
    }
  }
  const chart = new google.visualization.LineChart(document.getElementById('chart_div'))
  data.addColumn('datetime', 'Datetime')
  data.addColumn('number', 'Response Time')
  API(null, url, 'get').then(res => {
    let dataArray = []
    res.forEach(element => {
      let timestamp = new Date(element.timestamp);
      dataArray.push([timestamp, element.response_time])
    })
    data.addRows(dataArray)
    chart.draw(data, options)
  }).catch(alert)
}

function auth_login() {
  const email = document.getElementById("auth_email").value
  const password = document.getElementById("auth_password").value
  const method = 'POST'
  const url = '/api/login'
  const body = {
    email: email,
    password: password
  }
  API(body, url, method).then(_ => redirectToHome()).catch(alert)
}

function auth_logout() {
  const method = 'POST'
  const url = '/api/logout'
  API(null, url, method).then(_ => redirectToIndex()).catch(alert)
}

function change_password() {
  const currentPassword = document.getElementById("auth_current_password").value
  const newPassword = document.getElementById("auth_new_password").value
  const verifyPassword = document.getElementById("auth_verify_password").value
  if(!currentPassword || !newPassword || !verifyPassword) {
    alert('Please fill all fields!')
    return null
  }
  if(newPassword != verifyPassword) {
    alert('New password and verify password doesn\'t match!')
    return null
  }
  const method = 'POST'
  const body = {
    currentPassword: currentPassword,
    newPassword: newPassword,
    verifyPassword: verifyPassword
  }
  const url = '/api/change-password'
  API(body, url, method).then(_ => redirectToHome()).catch(alert)
}
