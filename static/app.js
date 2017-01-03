// Define the heimdallr module
var heimdallrApp = angular.module('heimdallrApp', ['ngAnimate']);

// Define the KillListController
heimdallrApp.controller('KillListController', function KillListController($scope, $http, $interval) {
  $scope.kms = []
  $scope.params = {'region': [10000035]}

  var getData = function() {
    $http.get("/search/"+JSON.stringify($scope.params))
    .then(function(response) {
      //$scope.kms = response.data;
      //Iterate through the response data and add them if they're new
      for(var i = 0; i < response.data.length; i++) {
        found = false;
        for(var ii = 0; ii < $scope.kms.length; ii++) {
          if(response.data[i].killID == $scope.kms[ii].killID) {
            found = true;
          }
        }
        if(found == false) {
          // Push the new object on to the km queue
          response.data[i].killmail.killTime = Date.parse(response.data[i].killmail.killTime)
          $scope.kms.push(response.data[i]);

          // If it's getting too large let's cull an object to avoid memory leaks
          if($scope.kms.length > 150) {
            $scope.kms.shift();
          }
        }
      }
    });
  }

  getData();
  $interval(function() {
    getData();
  }, 3000);


  /*var refreshData = function() {
    $http.get("/search/%7B%22minimumValue%22:500000000%7D")
    .then(function(response) {
      $scope.kms = response.data;
      $timeout(refreshData, 500);
    });
  }
  var promise = $timeout(refreshData, 500);*/


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
    if("alliance" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.finalBlow.alliance.id+"_64.png";
    } else if("corporation" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.finalBlow.corporation.id+"_64.png";
    } else {
      return "/static/img/eve-question.png"
    }
  }

  $scope.finalBlowName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.character.name;
    } else if("corporation" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.corporation.name;
    } else {
      return "?"
    }
  }

  $scope.finalBlowGuild = function(k) {
    r = ""
    if("corporation" in k.killmail.finalBlow) {
      r = r + k.killmail.finalBlow.corporation.name;
    }
    if("alliance" in k.killmail.finalBlow) {
      r = r + " / " + k.killmail.finalBlow.alliance.name;
    }
    if(r == "") {
      r = "?"
    }
    return r;
  }
});
