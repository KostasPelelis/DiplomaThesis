angular.module('netmode', [
	'ui.router', 
	'ngResource', 
	'admin',
	'templates.app',
])
.run(['$state', function($state){
	$state.go('admin.viewPolicies');
}]);