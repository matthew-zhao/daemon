angular.module('robot', ['ansible'])

.controller 'RobotStatusCtrl', [
  '$scope'
  '$interval' 
  'robotInfo'
  ($scope, $interval, robotInfo) -> 
    $scope.info = robotInfo()
    $interval(->
      $scope.info = robotInfo()
    , 5000)

  ]

