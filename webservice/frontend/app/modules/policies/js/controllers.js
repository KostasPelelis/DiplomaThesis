angular.module('netmode.policies.controllers', [])
.controller('PolicyController', ['$scope', 'Policy',
	function($scope, Policy) {
		$scope.policies = Policy.query();
	}
])
.controller('PolicyDetailsController', ['$stateParams', '$state', '$scope', 'Policy', 
	function($stateParams, $state, $scope, Policy){

		$scope.closePolicy = function() {
			$state.go('viewPolicies');
		}
		console.log($stateParams)
		$scope.singlePolicy = Policy.get({id: $stateParams.id});
	}
])