angular.module('adminModule', ['netmode.admin.controllers', 'netmode.admin.services'])
.config(['$stateProvider', '$locationProvider', function($stateProvider, $locationProvider) {
	$stateProvider.state('admin', {
		url: '/admin',
		abstraction: true,
		templateUrl: 'modules/admin/views/admin.tpl.html',
		controller: 'AdminController'
	})
	.state('admin.policyNew', {
		url: '/policies/new',
		templateUrl: 'modules/admin/views/policy-new.tpl.html',
		controller: 'PolicyNewController'
	})
	.state('admin.policyUpdate', {
		url: '/policies/:id/edit',
		templateUrl: 'modules/admin/views/policy-edit.tpl.html',
		controller: 'PolicyUpdateController'
	})
	.state('admin.viewPolicies', {
		url: '',
		templateUrl: 'modules/admin/views/policies-list.tpl.html',
		controller: 'PoliciesListController'
	});
}]);