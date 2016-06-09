/*
Copyright (C) 2012-2016  Luca Zanconato (<luca.zanconato@nharyes.net>)

This file is part of Plus Channel.

Plus Channel is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Plus Channel is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Plus Channel.  If not, see <http://www.gnu.org/licenses/>.
*/

(function(angular) {
'use strict';

    // controllers module
    var app = angular.module('app.controllers');

    app.controller('HomeCtrl', ['$scope', '$log', '$location', 'HomeService', function($scope, $log, $location, HomeService) {

        $scope.reset = function () {

            angular.element('#user-id-group').removeClass('has-error');
            angular.element('#user-id-group').removeClass('has-warning');
            $scope.loading = false;
            $scope.dataLoaded = false;
            $scope.feed = {};
            $scope.helpText = 'i.e. 117794718512661819956 or +Google';
            $scope.userId = '';
        };

        $scope.reset();

        $scope.getFeed = function() {

            angular.element('#user-id-group').removeClass('has-error');
            angular.element('#user-id-group').removeClass('has-warning');

            if (!$scope.userId || $scope.userId == '') {
                
                angular.element('#user-id-group').addClass('has-error');
                $scope.helpText = 'Please insert a User ID.';

            } else {

                angular.element('#user-id-group').addClass('has-warning');
                $scope.helpText = 'Loading profile information...';
                $scope.loading = true;

                // create feed
                HomeService.createFeed($scope.userId, function(response) {

                    $scope.loading = false;

                    // check status
                    if (response.status == 'KO') {

                        angular.element('#user-id-group').addClass('has-error');
                        $scope.helpText = response.error;

                    } else {

                        // display feed information
                        $scope.feed.photo = response.photo;
                        $scope.feed.name = response.name;
                        $scope.feed.url = $location.protocol() + "://" + location.host + '/feeds/' + response.pkey;
                        $scope.dataLoaded = true;
                    }

                }, function(error) {

                    /* ERROR */
                    $log.debug('Error: ' + error.statusText + '(' + error.status + ')');
                    angular.element('#user-id-group').addClass('has-error');
                    $scope.helpText = 'Internal error: please try again later.';

                    $scope.loading = false;
                });
            }
        };
    }]);

})(window.angular);
