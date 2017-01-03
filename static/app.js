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
    return numeral(isk).format('0,0.00a');
  }

  $scope.sysSecStatus = function(sec) {
    if(sec > 0 && sec <= 0.05) {
      return 0.1;
    } else {
      return numeral(sec).format('0.0');
    }
  }

  $scope.sysSecClass = function(sec) {
    if(sec > 0 && sec <= 0.05) {
      return "sec-0-1";
    } else {
      sec = Math.round(sec * 10) / 10;
      if(sec <= 0) {
        return "sec-0-0";
      } else {
        return "sec-" + numeral(sec).format('0.0').replace(".", "-");
      }
    }
  }

  $scope.victimIcon = function(k) {
    // Check if we have an alliance, otherwise just use the corporation
    if("alliance" in k.killmail.victim) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.victim.alliance.id+"_64.png";
    } else {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.victim.corporation.id+"_64.png";
    }
  }

  $scope.victimName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.victim) {
      return k.killmail.victim.character.name;
    } else {
      return k.killmail.victim.corporation.name;
    }
  }

  $scope.victimGuild = function(k) {
    r = k.killmail.victim.corporation.name;
    if("alliance" in k.killmail.victim) {
      r = r + " / " + k.killmail.victim.alliance.name;
    }
    return r;
  }

  $scope.finalBlowIcon = function(k) {
    // Check if we have an alliance otherwise, just use the corporation
    if("alliance" in k.killmail.attackers[0]) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.attackers[0].alliance.id+"_64.png";
    } else {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.attackers[0].corporation.id+"_64.png";
    }
  }
});
