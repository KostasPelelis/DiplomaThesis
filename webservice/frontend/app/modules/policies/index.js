angular.module('policiesModule', ['netmode.policies.controllers', 'netmode.policies.services'])
.config(['$stateProvider', '$locationProvider', function($stateProvider, $locationProvider) {
	$stateProvider.state('viewPolicies', {
		url: '/policies',
		templateUrl: 'modules/policies/views/policies.tpl.html',
		controller: 'PolicyController'
	});
	$stateProvider.state('singlePolicy', {
		url: 'policy/:id',
		templateUrl: 'modules/policies/views/policy.tpl.html',
		controller: 'PolicyDetailsController'
	})
}]);