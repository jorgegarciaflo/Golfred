var golfredApp = angular.module("golfredApp", ['ui.sortable']);

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


golfredApp.controller("modalActionCtrl", ['$scope','$http', function($scope, $http) {
	$scope.action_type="";
	$scope.action_representation="";
	$scope.addAction = function(uuid){		
		$scope.$emit('add_action',{'uuid':uuid,'type':$scope.action_type,'representation':$scope.action_representation});
	};
}]);



golfredApp.controller("modalGolemCtrl", ['$scope','$http', function($scope, $http) {
	$scope.position="None";
	$scope.processGolem = function(uuid){		
		$scope.$emit('process_golem',{'position':$scope.position,'uuid':uuid});
	};

	$scope.$on('position', function(event, args) {
		$scope.position=args['position'];
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
    $scope.read=true;
	$scope.fred=true;
	$scope.position="none";

	var formdata = new FormData();
	$scope.uploadFiles = function (uuid,$files) {
		for (var i = 0; i < $files.length; i++) {
			formdata.append("files", $files[i]);
		}
		$http.post('/api/add/memories/'+uuid,formdata,{
				withCredentials: true,
				headers: {'Content-Type': undefined },
				transformRequest: angular.identity,
				params: {'fred':$scope.fred,'analize':$scope.analize, 'read':$scope.read}
			})
			.success(function (d) {
				$scope.loadMemories(uuid);
			})
			.error(function () {
			});
	};


	$scope.saveOrder = function (uuid) {
			var order={};
			var i=0;
			for(memory in $scope.memories){
				order[$scope.memories[memory].id]=i;
				i=i+1;
			}
			var res = $http.post('/api/update/experience',{"uuid":uuid,
															"type":'order',
													       "order":JSON.stringify(order)});

	};

	$scope.candidateDelete = [];
	$scope.candidateGolem = [];

	$scope.deleteMemory = function(mem){		
			$scope.candidateDelete=mem;
	};

	$scope.getDescriptionText = function(rep){		
			var rep = JSON.parse(rep)
			if (rep.description){
				return rep.description.captions[0].text;
			}
	};


	$scope.getTags = function(rep){		
			var rep = JSON.parse(rep);
			var tags=[];
			if(rep.tags && rep.tags.length>0){
				for(tag in rep.tags.slice(0,5)){
					tag=rep.tags[tag];
					tags.push(tag.name);
				}
			return tags;
			}
	};

	$scope.getReadText = function(rep){		
			var rep = JSON.parse(rep);
			return rep.text;
	
	};


	$scope.processGolem = function(mem){		
			$scope.candidateGolem=mem;
			for(p in mem.perceptions){
				p=mem.perceptions[p];
				if(p.type=="golem"){
					$scope.$emit('position',{'pos':p.repr});
					break;
				}
			}
	};

	$scope.processFred = function(uuid,mem){		
			$scope.candidateDelete=mem;
			var res = $http.post('/api/update/memory',{"mem":mem.id.toString(),
														 "type":"fred"});
			$scope.loadMemories(uuid);
	};

	$scope.processRead = function(uuid,mem){		
			$scope.candidateDelete=mem;
			var res = $http.post('/api/update/memory',{"mem":mem.id.toString(),
														 "type":"read"});
			$scope.loadMemories(uuid);
	};

	$scope.processAnalysis = function(uuid,mem){		
			$scope.candidateDelete=mem;
			var res = $http.post('/api/update/memory',{"mem":mem.id.toString(),
														 "type":"analysis"});
			$scope.loadMemories(uuid);
	};

	$scope.addAction = function(uuid,type,representaion){		
			var res = $http.post('/api/push/memory',{
													 "uuid":uuid,
													 "type":"action",
													 "type2": type,
													 "representation":representation});
			$scope.loadMemories(uuid);
	};



	$scope.readMemory = function(mem){		
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


	$scope.processGolemReal = function(uuid,position,mem){
		var data = 	{"mem":mem.id,
												   "type":"golem",
													"position":position
													};
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
		$scope.saveOrder(uuid);
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

	$rootScope.$on('add_action', function(event, args) {
			type=args['type'];
			representation=args['representation'];
			uuid=args['uuid'];
			$scope.addAction(uuid,type,representation);
	});

	$rootScope.$on('delete_memory', function(event, args) {
			uuid=args['uuid'];
			$scope.deleteMemoryReal(uuid,$scope.candidateDelete);
	});

	$rootScope.$on('process_golem', function(event, args) {
			position=args['position'];
			uuid=args['uuid'];
			$scope.processGolemReal(uuid,position,$scope.candidateGolem);
	});




}]);


