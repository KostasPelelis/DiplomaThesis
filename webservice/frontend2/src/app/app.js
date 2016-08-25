angular.module('netmode', ['ui.router', 'ngResource', 'policiesModule', 'adminModule'])
.run(['$state', function($state){
	$state.go('viewPolicies');
}]);