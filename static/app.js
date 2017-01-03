// Define the heimdallr module
var heimdallrApp = angular.module('heimdallrApp', []);

// Define the KillListController
heimdallrApp.controller('KillListController', function KillListController($scope, $http) {
  $scope.kms = []
  $http.get("/search/%7B%22minimumValue%22:500000000%7D")
  .then(function(response) {
    $scope.kms = response.data;
  });

  // Display functions
  $scope.iskFormat = function(isk) {
    return numeral(isk).format('0,0.0a');
  }
});
