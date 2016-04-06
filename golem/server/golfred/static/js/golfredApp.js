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


golfredApp.controller("modalGolemCtrl", ['$scope','$http', function($scope, $http) {
	$scope.position="None";
	$scope.processGolem = function(){		
		$scope.$emit('process_golem',{'position':$scope.position});
	};

	$scope.$on('position', function(event, args) {
			$scope.position=args.position;
	});
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
	$scope.perceptions={};

	$scope.analize=true;
    $scope.cs=true;
	$scope.fred=true;
	$scope.position="none";

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
				transformRequest: angular.identity,
				params: {'fred':$scope.fred,'analize':$scope.analize, 'cs':$scope.cs}
			})
			.success(function (d) {
				$scope.loadMemories(uuid);
			})
			.error(function () {
			});
	};

	$scope.candidateDelete = [];
	$scope.candidateGolem = [];

	$scope.deleteMemory = function(mem){		
			$scope.candidateDelete=mem;
	};

	$scope.processGolem = function(mem){		
			$scope.candidateGolem=mem;
			$scope.$emit('position',{'pos':mem.position});
	};

	$scope.processFred = function(mem){		
			$scope.candidateDelete=mem;
			var res = $http.post('/api/update/memory/',{"mem":mem.id.toString(),
														 "type":"fred"});
			$scope.loadMemories(uuid);
	};

	$scope.readMemory = function(mem){		
		console.log(mem.id);
		var res = $http.post('/api/read/'+mem.id.toString());
	};

	$scope.deleteMemoryReal = function(uuid,mem){		
		var res = $http.post('/api/delete/memory',{"id":mem.id});
		res.success(function(data, status, headers, config) {
			$scope.loadMemories(uuid);
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		
	};


	$scope.processGolemReal = function(position,mem){
		var data = 	{"mem":mem.id,
												   "type":"golem",
													"position":position
													};
		console.log(data);
		var res = $http.post('/api/update/memory',data);
		res.success(function(data, status, headers, config) {
			$scope.loadMemories(uuid);
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		
	};



	$scope.changePerception = function(memoryid,perceptionid){
		for(memory in $scope.memories){
			memory=$scope.memories[memory];
			if(memory.id == memoryid){
				for (perception in memory.perceptions){
					perception=memory.perceptions[perception];
					if(perceptionid == perception.id){
						$scope.perceptions[memoryid]=perception.repr;
					}
				}			
		
			}
		}
	}		

	$scope.loadMemories = function(uuid){		
		$http.get('/api/list/memories/'+uuid).
			success(function(data, status, headers, config){
			$scope.memories = data;
			for(memory in $scope.memories){
				memory=$scope.memories[memory];
				if(!$scope.perceptions[memory.id]){
					$scope.perceptions[memory.id]=memory.perceptions[0].repr;
				}
			}
			})
		.error(function(error, status, headers, config) {
			alert( "failure message ");
		});		
	};

	$rootScope.$on('delete_memory', function(event, args) {
			uuid=args['uuid'];
			$scope.deleteMemoryReal(uuid,$scope.candidateDelete);
	});

	$rootScope.$on('process_golem', function(event, args) {
			position=args['position'];
			$scope.processGolemReal(position,$scope.candidateGolem);
	});




}]);


