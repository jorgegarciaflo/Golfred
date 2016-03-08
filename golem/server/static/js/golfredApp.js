var golfredApp = angular.module("golfredApp", []);

//golfredApp.controller('experienceCtrl', ['$scope', function($scope) {
//  $scope.greeting = 'Hola!';
//}]);



golfredApp.controller("experienceCtrl", ['$scope', '$http', function($scope, $http) {

	$scope.createExperience = function(){		

		console.log('Hello');
		var dataExperience = {
				name : $scope.name,
				description : $scope.description,
		};	

		var res = $http.post('/api/create');

		console.log('Request sent');

		res.success(function(data, status, headers, config) {
			$scope.message = data;
			alert( "Success: " + JSON.stringify({data: data}));
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		

		$scope.name='';
		$scope.description='';
	};

}]);


