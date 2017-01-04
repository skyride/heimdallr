// Define the heimdallr module
var heimdallrApp = angular.module('heimdallrApp', ['ngAnimate', 'ui.bootstrap']);

function mapID(arr) {
  return arr.map(function(item) {
    return item.id;
  });
}

// Define the KillsController
heimdallrApp.controller('KillsController', function KillsController($scope, $http, $interval) {
  $scope.kms = [];
  $scope.params = {
    "victimCharacter": [],
    "victimCorporation": [],
    "victimAlliance": [],
    "attackerCharacter": [],
    "attackerCorporation": [],
    "attackerAlliance": [],
    "victimShipType": [],
    "carrying": [],
    "solarSystem": [],
    "constellation": [],
    "region": [],
    "minimumValue": null
  };
  $scope.baseParams = JSON.parse(JSON.stringify($scope.params));

  var getData = function() {
    // Prune the param object from objects to ids
    params = JSON.parse(JSON.stringify($scope.params));
    for(var key in params) {
      if(key != "minimumValue") {
        params[key] = mapID(params[key]);
      }
    }

    $http.get("/search/"+JSON.stringify(params))
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


  // Autocomplete Feeds
  $scope.autoCompleteAlliance = function(search) {
    return $http.get("/autocomplete/alliance/"+search)
    .then(function(response) {
      return response.data;
    });
  };

  $scope.autoCompleteCorporation = function(search) {
    return $http.get("/autocomplete/corporation/"+search)
    .then(function(response) {
      return response.data;
    });
  };

  $scope.autoCompleteCharacter = function(search) {
    return $http.get("/autocomplete/character/"+search)
    .then(function(response) {
      return response.data;
    });
  };



  // Manipulate Filters
  // Alliance
  $scope.addVictimAlliance = function(item) {
    if(mapID($scope.params['victimAlliance']).indexOf(item.id) < 0) {
      $scope.params['victimAlliance'].push(item);
      $scope.kms = [];
      getData();
    }
  };
  $scope.removeVictimAlliance = function(item) {
    if(mapID($scope.params['victimAlliance']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimAlliance']).indexOf(item.id);
      $scope.params['victimAlliance'].splice(index, 1);
      $scope.kms = [];
      getData();
    }
  }

  // Corporation
  $scope.addVictimCorporation = function(item) {
    if(mapID($scope.params['victimCorporation']).indexOf(item.id) < 0) {
      $scope.params['victimCorporation'].push(item);
      $scope.kms = [];
      getData();
    }
  };
  $scope.removeVictimCorporation = function(item) {
    if(mapID($scope.params['victimCorporation']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimCorporation']).indexOf(item.id);
      $scope.params['victimCorporation'].splice(index, 1);
      $scope.kms = [];
      getData();
    }
  }

  //Character
  $scope.addVictimCharacter = function(item) {
    if(mapID($scope.params['victimCharacter']).indexOf(item.id) < 0) {
      $scope.params['victimCharacter'].push(item);
      $scope.kms = [];
      getData();
    }
  };
  $scope.removeVictimCharacter = function(item) {
    if(mapID($scope.params['victimCharacter']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimCharacter']).indexOf(item.id);
      $scope.params['victimCharacter'].splice(index, 1);
      $scope.kms = [];
      getData();
    }
  }

  $scope.resetFilters = function() {
    if(JSON.stringify($scope.params) !== JSON.stringify($scope.baseParams)) {
      $scope.params = JSON.parse(JSON.stringify($scope.baseParams));
      $scope.kms = [];
      getData();
    }
  };


  // Display functions
  $scope.iskFormat = function(isk) {
    return numeral(isk).format('0,0.00a');
  };

  $scope.sysSecStatus = function(sec) {
    if(sec > 0 && sec <= 0.05) {
      return 0.1;
    } else {
      return numeral(sec).format('0.0');
    }
  };

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
  };

  $scope.victimIcon = function(k) {
    // Check if we have an alliance, otherwise just use the corporation
    if("alliance" in k.killmail.victim) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.victim.alliance.id+"_64.png";
    } else {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.victim.corporation.id+"_64.png";
    }
  };

  $scope.victimName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.victim) {
      return k.killmail.victim.character.name;
    } else {
      return k.killmail.victim.corporation.name;
    }
  };

  $scope.victimGuild = function(k) {
    r = k.killmail.victim.corporation.name;
    if("alliance" in k.killmail.victim) {
      r = r + " / " + k.killmail.victim.alliance.name;
    }
    return r;
  };

  $scope.finalBlowIcon = function(k) {
    // Check if we have an alliance otherwise, just use the corporation
    if("alliance" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.finalBlow.alliance.id+"_64.png";
    } else if("corporation" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.finalBlow.corporation.id+"_64.png";
    } else {
      return "/static/img/eve-question.png"
    }
  };

  $scope.finalBlowName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.character.name;
    } else if("corporation" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.corporation.name;
    } else {
      return "?"
    }
  };

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
  };
});
