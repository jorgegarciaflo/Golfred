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
			alert( "Error: " + data.msg);
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

	$rootScope.$on('delete_experience', function(event, args) {
			$scope.deleteExperienceReal($scope.candidateDelete);
	});

	$scope.loadExperiences();


}]);

golfredApp.controller("modalCreateCtrl", ['$scope','$http', function($scope, $http) {
	
	$scope.createExperience = function(isValid){		
		var dataExperience = {
				name : $scope.name,
				description : $scope.description,
		};	

		console.log(isValid);
		if(isValid){
			var res = $http.post('/api/create/experience',dataExperience);
			res.success(function(data, status, headers, config) {
				if(data.status=="ok"){
					$scope.$emit('reload',{});
				}else{
					alert( "Error: " + JSON.stringify({data: data}));
				}
			});

			res.error(function(data, status, headers, config) {
				alert( "failure message: " + JSON.stringify({data: data}));
			});		
		}

		$scope.name='';
		$scope.description='';
	};

}]);

golfredApp.controller("modalDeleteCtrl", ['$scope','$http', function($scope, $http) {
	$scope.deleteExperience = function(){		
		$scope.$emit('delete_experience',{});
	};
	
	$scope.deleteEvent = function(uuid){		
		$scope.$emit('delete_event',{'uuid':uuid});
	};
}]);


golfredApp.controller("modalActionCtrl", ['$scope','$http', function($scope, $http) {
$scope.addAction = function(uuid,isValid){
		if(isValid){
			$scope.$emit('add_action',{'uuid':uuid,'type':$scope.action_type,'command':$scope.action_command,'args':$scope.action_args});
		}
	};
	$scope.action_type="";
	$scope.action_command="";
	$scope.action_args="";
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

golfredApp.controller("eventCtrl", ['$scope', '$rootScope','$http', function($scope,$rootScope,$http) {

	$scope.events = [];
	$scope.infos={};

	$scope.options={
		'analize':true,
        'read':true,
		'fred':false
	}

	var formdata = new FormData();
	$scope.uploadFiles = function (uuid,$files) {
		for (var i = 0; i < $files.length; i++) {
			formdata.append("files", $files[i]);
		}
		$http.post('/api/add/events/'+uuid,formdata,{
				withCredentials: true,
				headers: {'Content-Type': undefined },
				transformRequest: angular.identity,
				params: {'fred':$scope.options.fred,'analize':$scope.options.analize, 'read':$scope.options.read}
			})
			.success(function (d) {
				$scope.loadEvents(uuid);
			})
			.error(function () {
			});
	};


	$scope.saveOrder = function (uuid) {
			var order={};
			var i=0;
			if($scope.events.length>0){
				for(event in $scope.events){
					order[$scope.events[event].id]=i;
					i=i+1;
				}
				var res = $http.post('/api/update/experience',{"uuid":uuid,
															"type":'order',
													       "order":JSON.stringify(order)});
			}
	};

	$scope.candidateDelete = [];
	$scope.candidateGolem = [];

	$scope.deleteEvent = function(mem){		
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
			for(p in mem.infos){
				p=mem.infos[p];
				if(p.type=="golem"){
					$scope.$emit('position',{'pos':p.repr});
					break;
				}
			}
	};

	$scope.processRead = function(uuid,e){		
			var res = $http.post('/api/update/info',{"eid":e.id.toString(),
													  "type":"read"});
			$scope.loadEvents(uuid);
	};

	$scope.processAnalysis = function(uuid,e){		
			var res = $http.post('/api/update/info',{"eid":e.id.toString(),
													 "type":"analysis"});
			$scope.loadEvents(uuid);
	};

	$scope.addAction = function(args){		
			var res = $http.post('/api/push/event',{
													 "uuid":args['uuid'],
													 "type":"action",
													 "type_action": args['type'],
													 "args": args['args'],
													 "command":args['command']});
			$scope.loadEvents(args['uuid']);
	};



	$scope.readEvent = function(mem){		
		var res = $http.post('/api/read/'+mem.id.toString());
	};

	$scope.deleteEventReal = function(uuid,mem){		
		var res = $http.post('/api/delete/event',{"id":mem.id});
		res.success(function(data, status, headers, config) {
			$scope.loadEvents(uuid);
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
		var res = $http.post('/api/update/event',data);
		res.success(function(data, status, headers, config) {
			$scope.loadEvents(uuid);
		});

		res.error(function(data, status, headers, config) {
			alert( "failure message: " + JSON.stringify({data: data}));
		});		
	};


	$scope.changeInfo = function(eid,iid){
		for(e in $scope.events){
			e=$scope.events[e];
			if(e.id == eid){
				for (i in e.infos){
					i=e.infos[i];
					if(iid == i.id){
						$scope.infos[eid]=i.json;
					}
				}			
		
			}
		}
	}		

	$scope.loadEvents = function(uuid){
		$scope.saveOrder(uuid);
		$http.get('/api/list/events/'+uuid).
			success(function(data, status, headers, config){
			$scope.events = data;
			for(e in $scope.events){
				e=$scope.events[e];
				if(!$scope.infos[e.id]){
					$scope.infos[e.id]=e.infos[0].json;
				}
			}
			})
		.error(function(error, status, headers, config) {
			alert( "Error "+error.msg);
		});		
	};

	$rootScope.$on('add_action', function(event, args) {
			$scope.addAction(args);
	});

	$rootScope.$on('delete_event', function(event, args) {
			uuid=args['uuid'];
			$scope.deleteEventReal(uuid,$scope.candidateDelete);
	});

	$rootScope.$on('process_golem', function(event, args) {
			position=args['position'];
			uuid=args['uuid'];
			$scope.processGolemReal(uuid,position,$scope.candidateGolem);
	});




}]);


