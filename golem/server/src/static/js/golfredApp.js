var golfredApp = angular.module("golfredApp", []);

//golfredApp.controller('experienceCtrl', ['$scope', function($scope) {
//  $scope.greeting = 'Hola!';
//}]);

golfredApp.config(['$interpolateProvider', function($interpolateProvider) {
	  $interpolateProvider.startSymbol('{[');
		    $interpolateProvider.endSymbol(']}');
}]);
	

golfredApp.controller("experienceCtrl", ['$scope', '$rootScope', '$http', function($scope, $rootScope,$http) {

	$scope.experiences = [];
	$scope.candidateDelete = [];

	$scope.deleteExperience = function(exp){		
			$scope.candidateDelete=exp;
	};

	$scope.deleteExperienceReal = function(exp){		
		var res = $http.post('/api/delete/experience',{"uuid":exp.uuid});
		res.success(function(data, status, headers, config) {
			$scope.loadExperiences();
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		
	};

	$scope.loadExperiences = function(){		
		$http.get('/api/latest/experiences/5').
			success(function(data, status, headers, config){
			$scope.experiences = data;
		})
		.error(function(error, status, headers, config) {
			alert( "failure message ");
		});		
	};

	$rootScope.$on('reload', function(event, args) {
			$scope.loadExperiences();
	});

	$rootScope.$on('delete_expereince', function(event, args) {
			$scope.deleteExperienceReal($scope.candidateDelete);
	});

	$scope.loadExperiences();


}]);

golfredApp.controller("modalCreateCtrl", ['$scope','$http', function($scope, $http) {
	$scope.createExperience = function(){		
		var dataExperience = {
				name : $scope.name,
				description : $scope.description,
		};	

		var res = $http.post('/api/create',dataExperience);
		res.success(function(data, status, headers, config) {
			$scope.$emit('reload',{});
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		

		$scope.name='';
		$scope.description='';
	};

}]);

golfredApp.controller("modalDeleteCtrl", ['$scope','$http', function($scope, $http) {
	$scope.deleteExperience = function(){		
		$scope.$emit('delete_experience',{});
	};
	
	$scope.deleteMemory = function(uuid){		
		$scope.$emit('delete_memory',{'uuid':uuid});
	};
}]);

golfredApp.directive('ngFiles', ['$parse', function ($parse) {
	function fn_link(scope, element, attrs) {
		var onChange = $parse(attrs.ngFiles);
		element.on('change', function (event) {
			onChange(scope, { $files: event.target.files });
		});
	};

	return {
			link: fn_link
	}
}])

golfredApp.controller("memoryCtrl", ['$scope', '$rootScope','$http', function($scope,$rootScope,$http) {

	$scope.memories = [];

	var formdata = new FormData();
	$scope.getTheFiles = function ($files) {
		for (var i = 0; i < $files.length; i++) {
			formdata.append("files", $files[i]);
		}
	};

	$scope.uploadFiles = function (uuid) {
		$http.post('/api/add/memories/'+uuid,formdata,{
				withCredentials: true,
				headers: {'Content-Type': undefined },
				transformRequest: angular.identity
			})
			.success(function (d) {
				$scope.loadMemories(uuid);
			})
			.error(function () {
			});
	};


	$scope.candidateDelete = [];

	$scope.deleteMemory = function(mem){		
			$scope.candidateDelete=mem;
	};


	$scope.readMemory = function(mem){		
		console.log(mem.id);
		var res = $http.post('/api/read/'+mem.id.toString());
	
	};


	$scope.deleteMemoryReal = function(uuid,mem){		
		console.log(mem)
		var res = $http.post('/api/delete/memory',{"id":mem.id});
		res.success(function(data, status, headers, config) {
			$scope.loadMemories(uuid);
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		
	};

	$scope.loadMemories = function(uuid){		
		$http.get('/api/list/memories/'+uuid).
			success(function(data, status, headers, config){
			$scope.memories = data;
		})
		.error(function(error, status, headers, config) {
			alert( "failure message ");
		});		
	};

	$rootScope.$on('delete_memory', function(event, args) {
			uuid=args['uuid']
			$scope.deleteMemoryReal(uuid,$scope.candidateDelete);
	});


}]);


