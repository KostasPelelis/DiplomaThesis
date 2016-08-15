angular.module('netmode.policies.services', [])
.factory('Policy', ['$resource', 'API_ENDPOINT', function ($resource, API_ENDPOINT){
	return $resource(API_ENDPOINT, {id: '@id'}, {
		update: {
			method: 'PUT'
		},
		save: {
			method: 'POST',
			params: {from_json: true}
		}
	})
}])
.value('API_ENDPOINT', 'http://127.0.0.1:9090/api/v1/policies/:id');