var videosApp = angular.module('videosApp');

videosApp.controller('navController', function ($scope, $http, $location, Auth, Constants) {
  console.log('loading navController');
  $scope.Auth = Auth;
  $scope.logout = function () {
    $http.get(url = '/api/logout').then(
      function (response) {
        Auth.setAuthStatus(Constants.authStatus.loggedout);
        Auth.goto('/list/', null);
      },
      function (response) {
        // do nothing
      }
    );
  };
});

videosApp.controller(
  'loginController',
  function ($scope, $http, $location, $resource, Auth, Constants) {

    $scope.create = function () {
      $location.path('createuser');
    };

    Login = $resource('/api/login/');
    $scope.login = function () {
      var data = { username: $scope.username, password: $scope.password };
      var login = new Login(data);
      login.$save(
        function (response) {
          if (response.result == 'success') {
            Auth.checkAuthStatus();
            Auth.gotoNext();
          } else if (response.result == 'invalid') {
            $scope.result = 'User is inactive!';
          } else if (response.result == 'failure') {
            $scope.result = 'Username or password incorrect!';
          }
        },
        function (response) {
          $scope.result = 'Permission denied, please contact site administrator.';
        }
      );
    };
  }
);

videosApp.controller(
  'createUserController',
  function ($scope, $http, $location, $resource, Auth, Constants) {

    $scope.create = function () {
      if ($scope.password != $scope.password2) {
        $scope.result = 'Passwords must match!';
        return;
      }

      var data = {
        username: $scope.username,
        password: $scope.password,
        email: $scope.email,
      };

      AddUser = $resource('/api/add_user/');
      newUser = new AddUser(data);
      newUser.$save(
        function (response) {
          if (response.result == 'success') {
            Auth.checkAuthStatus();
            Auth.gotoNext();
          } else {
            if ('username' in response.errors) {
              $scope.result = response.errors.username[0].message;
            } else if ('password' in response.errors) {
              $scope.result = response.errors.password[0].message;
            } else if ('email' in response.errors) {
              $scope.result = response.errors.email[0].message;
            } else {
              $scope.result = 'Failure!';
            }
          }
        },
        function (response) {
          $scope.result = 'Permission denied, please try again.';
        }
      );
    };
  }
);

videosApp.controller(
  'listController',
  function ($scope, $http, $location, uiGridConstants, Auth, Constants, UserVideo, videoData) {

    $scope.Auth = Auth;

    console.log('loading listController');
    var templateBegin = '<button ng-if="!row.entity.user_added" ';
    var templateEnd = 'ng-click="grid.appScope.addVideo(row.entity)">Add</button>';
    var cellTemplate = templateBegin + templateEnd;

    var columnDefs = [
      { field: 'created_at' },
      { field: 'name' },
      { field: 'description' },
      { field: 'credits' },
    ];
    if (Auth.subscribed()) {
      var columnDefsEnd = [
        { field: 'percent_watched' },
        { field: 'credits_awarded' },
        { field: 'add_video', name: ' ', width: 50,
          enableFiltering: false, enableSorting: false, cellTemplate: cellTemplate, }
      ];
      columnDefs = columnDefs.concat(columnDefsEnd);
    }

    $scope.gridOptions = {
      enableSorting: true,
      enableFiltering: true,
      columnDefs: columnDefs,
    };

    $scope.gridOptions.onRegisterApi = function (gridApi) {
      //set gridApi on scope
      $scope.gridApi = gridApi;
    };

    var transformData = function () {
      var len = $scope.gridOptions.data.length;
      for (var i = 0; i < len; i++) {
        var createdAt = moment($scope.gridOptions.data[i].created_at);
        $scope.gridOptions.data[i].created_at = createdAt.format('YYYY-MM-DD HH:mm');
        var userVideo = $scope.gridOptions.data[i].user_video;
        $scope.gridOptions.data[i].percent_watched = userVideo ? userVideo.percent_watched : 0;
        $scope.gridOptions.data[i].credits_awarded = userVideo ? userVideo.credits_awarded : 0;
        $scope.gridOptions.data[i].user_added = userVideo ? userVideo.active : false;
      }
    };

    $scope.addVideo = function (rowEntity) {
      if (rowEntity.user_video) {
        var uservideo = UserVideo.get(
          { uservideoId: rowEntity.user_video.id },
          function () {
            rowEntity.user_added = true;
            uservideo.active = true;
            uservideo.$update();
          }
        );
      } else {
        var params = {
          user_id: Auth.getUserId(),
          video_id: rowEntity.id,
        };
        var newUserVideo = new UserVideo(params);
        newUserVideo.$save(function (user, putResponseHeaders) {
            rowEntity.user_added = true;
          }
        );
      }
    };

    $scope.gridOptions.data = videoData;
    transformData();
    $scope.showGrid = true;
  }
);

videosApp.controller(
  'myVideosController',
  function ($scope, $http, $location, $resource, Auth, Constants, UserVideo, uservideoData) {

    console.log('loading myVideosController');
    watchCellTemplate = '<a href="#/viewvideo/{{ row.entity.id }}">Watch</a>';
    removeCellTemplate = '<button ng-click="grid.appScope.removeVideo(row.entity)">Remove</button>';

    $scope.gridOptions = {
      enableSorting: true,
      enableFiltering: true,
      columnDefs: [
        { field: 'subscribed_at' },
        { field: 'video.name', name: 'Name' },
        { field: 'video.description', name: 'Description' },
        { field: 'video.credits', name: 'Credits' },
        { field: 'percent_watched' },
        { field: 'credits_awarded' },
        { field: 'watch', name: ' ', width: 50,
          enableFiltering: false, enableSorting: false, cellTemplate: watchCellTemplate, },
        { field: 'remove', name: '  ', width: 80,
          enableFiltering: false, enableSorting: false, cellTemplate: removeCellTemplate, },
      ],
    };

    var transformData = function () {
      var len = $scope.gridOptions.data.length;
      for (var i = 0; i < len; i++) {
        var subscribedAt = moment($scope.gridOptions.data[i].subscribed_at);
        $scope.gridOptions.data[i].subscribed_at = subscribedAt.format('YYYY-MM-DD HH:mm');
      }
    };

    $scope.removeVideo = function (rowEntity) {
      var uservideo = UserVideo.get({ uservideoId: rowEntity.id }, function () {
        uservideo.active = false;
        uservideo.$update();
        var len = $scope.gridOptions.data.length;
        for (var i = 0; i < len; i++) {
          if ($scope.gridOptions.data[i].id == rowEntity.id) {
            $scope.gridOptions.data.splice(i, 1);
          }
        }
      });
    };

    $scope.gridOptions.data = uservideoData;
    transformData();
    $scope.showGrid = true;
  }
);

videosApp.controller(
  'viewVideoController',
  function ($scope, $http, $location, $resource, $routeParams, Auth, Constants, uservideoData) {
    console.log('loading viewVideoController');

    $scope.uservideo = uservideoData[0];
    $scope.youtube_id = $scope.uservideo.video.youtube_id;
    $scope.checkLengthScheduled = false;

    $scope.$on('youtube.player.playing', function ($event, player) {
      var checkLengthPlayed = function () {
        var lengthPlayed = player.getCurrentTime();
        if ($scope.uservideo.length_watched < lengthPlayed) {
          $scope.uservideo.length_watched = Math.round(lengthPlayed);
          $scope.uservideo.$update();
        }

        if (player.getPlayerState() == 1) {
          setTimeout(checkLengthPlayed, 10 * 1000);
        } else {
          $scope.checkLengthScheduled = false;
        }
      };

      if (!$scope.checkLengthScheduled) {
        $scope.checkLengthScheduled = true;
        setTimeout(checkLengthPlayed, 10 * 1000);
      }
    });
  }
);

videosApp.controller(
  'badgesController',
  function ($scope, $location, $resource, Auth, Constants, userbadgeData, usercreditData) {
    $scope.gridOptions = {
      enableSorting: false,
      enableFiltering: false,
      columnDefs: [
        { field: 'award_month' },
        { field: 'badge.name', name: 'Name' },
        { field: 'badge.description', name: 'Description' },
        { field: 'badge.credits_required', name: 'Credits Required' },
      ],
    };

    $scope.credits = usercreditData.data.credits;
    $scope.gridOptions.data = userbadgeData;
    $scope.showGrid = true;
  }
);

videosApp.controller(
  'mySubscriptionController',
  function ($scope, $http, $location, $resource, $route, Auth, Constants, userData) {
    $scope.subscription = userData.data[0].subscription;
    var paidFrom = moment($scope.subscription.paid_from);
    $scope.subscription.paid_from = paidFrom.format('YYYY-MM-DD HH:mm');
    var paidUntil = moment($scope.subscription.paid_until);
    $scope.subscription.paid_until = paidUntil.format('YYYY-MM-DD HH:mm');

    $scope.cancelSubscription = function () {
      $http.get('/api/cancel_subscription/').then(function (response) {
          $route.reload();
        }
      );
    };
  }
);

videosApp.controller(
  'subscribeController',
  function ($scope, $http, $location, $resource, Auth, Constants, subscriptionTypeData) {
      $scope.subscriptionTypes = subscriptionTypeData;
  }
);
