angular.module('netmode.admin.policiescrud', [])
.controller('PolicyNewController', ['$scope', '$state',
	function($scope, $state, Policy){
		$scope.policy = {
			name: '',
			event: {name: '', arguments: []},
			conditions: [],
			action: null
		}
		
		$scope.addCondition = function(condition) {
			var newCondition = angular.copy(condition);
			$scope.policy.conditions.push(newCondition);
			condition = {};
		}

		$scope.buttonText = 'Create';
		
		$scope.savePolicy = function() {
			$('#policy-submit').addClass('loading');
			$('#new-policy-error-message').fadeIn();
			$scope.policy.$save(function() {
				$('#policy-submit').removeClass('loading');
				$state.go('admin.viewPolicies');
			}, function(error) {
				$('#policy-submit').removeClass('loading');
				$('#new-policy-error-message').fadeIn('slow');
			})
		}

		$scope.closeMessage = function() {
			$('#new-policy-error-message').fadeOut('slow');
		}
	}
])
.controller('PolicyUpdateController', ['$scope', 'Policy', '$stateParams', '$state',
	function($scope, Policy, $stateParams, $state){
		$scope.policy = Policy.get({id: $stateParams.id});
		$scope.buttonText = 'Update';

		$scope.addCondition = function(condition) {
			var newCondition = angular.copy(condition);
			$scope.policy.conditions.push(newCondition);
			condition = {};
		}
	
		$scope.updatePolicy = function() {
			$('#policy-submit').addClass('loading');
			$scope.policy.$update(function(data){
				$state.go('admin.viewPolicies')
				$('#policy-submit').removeClass('loading');
			},function(error){
				$('#policy-submit').removeClass('loading')
			})
		}
	}
])
.controller('PoliciesListController', ['$scope', 'popupService', '$state',
	function($scope, popupService, $state){
		$scope.policies = [];
		$scope.deletePolicy = function(policy) {
			console.log('Deleting', policy)
			if (popupService.showPopup("Really delete this?")) {
				policy.$delete(function() {
					$state.go('admin.viewPolicies', undefined, {
						reload: true
					});
				})
			}
		}
	}
])