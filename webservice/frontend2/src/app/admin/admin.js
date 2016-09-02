angular.module('admin', ['netmode.popupService', 'netmode.admin.policiescrud'])
.config(['$stateProvider', function($stateProvider) {
	$stateProvider.state('admin', {
		url: '/admin',
		abstraction: true,
		templateUrl: 'admin/admin.tpl.html',
		controller: 'AdminController'
	})
	.state('admin.policyNew', {
		url: '/policies/new',
		templateUrl: 'admin/policy-new.tpl.html',
		controller: 'PolicyNewController'
	})
	.state('admin.policyUpdate', {
		url: '/policies/:id/edit',
		templateUrl: 'admin/policy-edit.tpl.html',
		controller: 'PolicyUpdateController'
	})
	.state('admin.viewPolicies', {
		url: '',
		templateUrl: 'admin/policies-list.tpl.html',
		controller: 'PoliciesListController'
	});
}])
.controller('AdminController', ['$scope', '$state',
	function($scope, $state){
		$state.go('admin.viewPolicies');
	}
]);