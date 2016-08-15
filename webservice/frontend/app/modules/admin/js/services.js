angular.module('netmode.admin.services', [])
.service('popupService', ['$window', function($window){
	this.showPopup = function(message) {
		return $window.confirm(message);
	}
}])