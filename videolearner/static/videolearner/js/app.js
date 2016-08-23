var videosApp = angular.module(
  'videosApp', ['ngRoute', 'ngResource', 'ui.grid', 'youtube-embed']);

videosApp.constant('Constants', {
  authStatus: {
    loggedout: 0,
    loggedin: 1,
    confirmed: 2,
    subscribed: 3,
  },
});

videosApp.config(function ($routeProvider, $httpProvider, $resourceProvider) {
    $routeProvider
    .when('/login', {
      templateUrl: '/static/videolearner/html/partials/login.html',
      controller: 'loginController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.shouldLoadPage(
            Constants.authStatus.loggedout, null
          );
        },
      },
    })
    .when('/createuser', {
      templateUrl: '/static/videolearner/html/partials/createuser.html',
      controller: 'createUserController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.shouldLoadPage(
            Constants.authStatus.loggedout, null
          );
        },
      },
    })
    .when('/list', {
      templateUrl: '/static/videolearner/html/partials/list.html',
      controller: 'listController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.checkAuthStatus();
        },
        videoData: function (Video) {
          var videoData = Video.query();
          return videoData.$promise;
        },
      },
    })
    .when('/subscribe', {
      templateUrl: '/static/videolearner/html/partials/subscribe.html',
      controller: 'subscribeController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.shouldLoadPage(
            Constants.authStatus.confirmed, '/subscribe/'
          );
        },
        subscriptionTypeData: function (SubscriptionType) {
          var subscriptionTypeData = SubscriptionType.query();
          return subscriptionTypeData.$promise;
        },
      },
    })
    .when('/myvideos', {
      templateUrl: '/static/videolearner/html/partials/myvideos.html',
      controller: 'myVideosController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.shouldLoadPage(
            Constants.authStatus.subscribed, '/myvideos/'
          );
        },
        uservideoData: function (UserVideo) {
          var uservideoData = UserVideo.query({ active: true });
          return uservideoData.$promise;
        },
      },
    })
    .when('/viewvideo/:uservideoId', {
      templateUrl: '/static/videolearner/html/partials/viewvideo.html',
      controller: 'viewVideoController',
      resolve: {
        load: function (Auth, Constants, $route) {
          var next = '/viewvideo/' + $route.current.params.videoId + '/';
          return Auth.shouldLoadPage(
            Constants.authStatus.subscribed, next
          );
        },
        uservideoData: function ($route, UserVideo) {
          var uservideoId = $route.current.params.uservideoId;
          var uservideoData = UserVideo.query({ id: uservideoId, active: true });
          return uservideoData.$promise;
        },
      },
    })
    .when('/badges', {
      templateUrl: '/static/videolearner/html/partials/badges.html',
      controller: 'badgesController',
      resolve: {
        load: function (Auth, Constants) {
          return Auth.shouldLoadPage(
            Constants.authStatus.subscribed, '/badges/'
          );
        },
        userbadgeData: function (UserBadge) {
          var userbadgeData = UserBadge.query();
          return userbadgeData.$promise;
        },
        usercreditData: function ($http) {
          return $http.get('/api/credits/');
        },
      },
    })
    .when('/mysubscription', {
      templateUrl: '/static/videolearner/html/partials/mysubscription.html',
      controller: 'mySubscriptionController',
      resolve: {
        load: function (Auth, Constants) {
          if (Auth.getAuthStatus() == Constants.authStatus.confirmed &&
              Auth.getSubscription() != null) {
            return true;
          }
          return Auth.shouldLoadPage(Constants.authStatus.subscribed, '/mysubscription/');
        },
        userData: function ($http) {
          return $http.get('/api/userprofile/');
        },
      },
    })
    .otherwise({ redirectTo: '/list' });

    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';

    $resourceProvider.defaults.stripTrailingSlashes = false;
  }
);
