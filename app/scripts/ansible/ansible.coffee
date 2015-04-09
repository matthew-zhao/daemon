angular.module('ansible', [])

.service 'ansible', ->

  HOSTNAME = '10.31.1.61'
  PORT = 12345
  socket = io("http://#{HOSTNAME}:#{PORT}")

  return socket

.service 'robotInfo', ->
  return -> {
    battery: 0.6,
    wireless_strength: 0.7
  }