angular.module('admin', ['netmode.popupService', 'netmode.admin.policiescrud'])
.config(['$stateProvider', function($stateProvider) {
	$stateProvider.state('admin', {
		url: '/admin',
		abstraction: true,
		templateUrl: 'app/admin/admin.tpl.html',
		controller: 'AdminController'
	})
	.state('admin.policyNew', {
		url: '/policies/new',
		templateUrl: 'app/admin/policy-new.tpl.html',
		controller: 'PolicyNewController'
	})
	.state('admin.policyUpdate', {
		url: '/policies/:id/edit',
		templateUrl: 'app/admin/policy-edit.tpl.html',
		controller: 'PolicyUpdateController'
	})
	.state('admin.viewPolicies', {
		url: '',
		templateUrl: 'app/admin/policies-list.tpl.html',
		controller: 'PoliciesListController'
	});
}])
.controller('AdminController', ['$scope', '$state',
	function($scope, $state){
		$state.go('admin.viewPolicies');
	}
]);