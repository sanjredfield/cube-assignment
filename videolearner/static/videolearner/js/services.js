var videosApp = angular.module('videosApp');

videosApp.factory('SubscriptionType', ['$resource', function ($resource) {
    return $resource('/api/subscriptiontype/:subscriptiontypeId/', { subscriptiontypeId: '@id' });
  },
]);

videosApp.factory('Video', ['$resource', function ($resource) {
    return $resource('/api/video/:videoId/', { videoId: '@id' });
  },
]);

videosApp.factory('UserBadge', ['$resource', function ($resource) {
    return $resource('/api/userbadge/:userbadgeId/', { userbadgeId: '@id' });
  },
]);

videosApp.factory('UserVideo', ['$resource', function ($resource) {
    return $resource(
      '/api/uservideo/:uservideoId/',
      { uservideoId: '@id' },
      { update: { method: 'PUT' }, }
    );
  },
]);

videosApp.factory('Auth', function ($http, $location, $rootScope, $q, Constants) {
    var authStatus = window.authStatus;
    var userUrl = window.userUrl;
    var userId = window.userId;
    var subscription = window.subscription;

    var service = {
      getAuthStatus: function () {
        return authStatus;
      },

      setAuthStatus: function (_authStatus) {
        authStatus = _authStatus;
        window.authStatus = _authStatus;
      },

      setUserUrl: function (_userUrl) {
        userUrl = _userUrl;
        window.userUrl = _userUrl;
      },

      getUserUrl: function () {
        return userUrl;
      },

      setUserId: function (_userId) {
        userId = _userId;
        window.userId = _userId;
      },

      getUserId: function () {
        return userId;
      },

      setSubscription: function (_subscription) {
        subscription = _subscription;
        window.subscription = _subscription;
      },

      getSubscription: function () {
        return subscription;
      },

      loggedin: function () {
        return authStatus >= Constants.authStatus.loggedin;
      },

      loggedout: function () {
        return authStatus == Constants.authStatus.loggedout;
      },

      confirmed: function () {
        return authStatus >= Constants.authStatus.confirmed;
      },

      subscribed: function () {
        return authStatus == Constants.authStatus.subscribed;
      },

      goto: function (path, next) {
        $location.path(path);
        $location.search('next', next);
      },

      gotoNext: function () {
        var next = '/list';
        if ('next' in $location.search()) {
          next = $location.search().next;
          $location.search('next', null);
        }

        $location.path(next);
      },

      checkAuthStatus: function () {
        return new Promise(
          function (resolve, reject) {
            $http.get('/api/userprofile/').then(
              function (response) {
                var user = response.data[0];
                service.setUserUrl(user.url);
                service.setUserId(user.id);
                service.setSubscription(user.subscription);
                if (user.valid_subscription) {
                  service.setAuthStatus(Constants.authStatus.subscribed);
                } else if (user.email_confirmed) {
                  service.setAuthStatus(Constants.authStatus.confirmed);
                } else {
                  service.setAuthStatus(Constants.authStatus.loggedin);
                }
                resolve();
              },
              function (response) {
                service.setAuthStatus(Constants.authStatus.loggedout);
                service.setUserUrl(null);
                service.setUserId(null);
                service.setSubscription(null);
                resolve();
              }
            );
          }
        );
      },

      shouldLoadPage: function (authRequirement, next) {
        var defer = $q.defer();
        var checkAuth = function () {
          if (authStatus == authRequirement) {
            defer.resolve();
          } else if (authStatus == Constants.authStatus.loggedout) {
            service.goto('/login/', next);
            defer.reject();
          } else {
            service.goto('/list/', null);
            defer.reject();
          }
        };

        service.checkAuthStatus().then(checkAuth, checkAuth);
        return defer.promise;
      },
    };
    return service;
  }
);
