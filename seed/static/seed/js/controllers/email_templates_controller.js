// /**
//  * :copyright (c) 2014 - 2020, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
//  * :author
//  */

angular.module('BE.seed.controller.email_templates', [])
    .controller('email_templates_controller', [
        '$scope', //from before
        'organization_payload',
        'postoffice_service',
        '$uibModal',
        'urls',
        //     '$uibModalInstance', //?
        //     'action', //new_group
        //     'group_service', //from before
        //     'inventory_service', //from before
        //     //'settings_location',
        //     'inventory_type', //new_group
        //     'data', //new_group
        //     'org_id', //new_group
        function (
            $scope,
            organization_payload,
            postoffice_service,
            $uibModal,
            urls,
            //       $uibModalInstance,
            //       action,
            //       group_service,
            //       inventory_service,
            //       //settings_location,
            //       inventory_type,
            //       data,
            //       org_id
        ) {
            $scope.org = organization_payload.organization;
            $scope.available_templates = [];
            postoffice_service.get_templates().then(function (templates) {
                $scope.available_templates = templates;
            });
            $scope.renameTemplate = function () {
                var oldTemplate = angular.copy($scope.dropdown_selected_template);

                var modalInstance = $uibModal.open({
                    templateUrl: urls.static_url + 'seed/partials/email_templates_modal.html',
                    // controller: 'email_templates_modal_controller',
                    resolve: {
                        action: _.constant('rename'),
                        data: _.constant($scope.dropdown_selected_template),
                    }
                });

                modalInstance.result.then(function (newName) {
                    $scope.dropdown_selected_template.name = newName;
                    _.find($scope.available_templates, { id: $scope.dropdown_selected_template.id }).name = newName;
                    Notification.primary('Renamed ' + oldTemplate.name + ' to ' + newName);
                });
            };
            $scope.removeTemplate = function () {
                var oldTemplate = angular.copy($scope.dropdown_selected_template);
        
                var modalInstance = $uibModal.open({
                  templateUrl: urls.static_url + 'seed/partials/email_templates_modal.html',
                //   controller: 'email_templates_modal_controller',
                  resolve: {
                    action: _.constant('remove'),
                    data: _.constant($scope.dropdown_selected_template),
                  }
                });
        
                modalInstance.result.then(function () {
                  _.remove($scope.available_templates, oldTemplate);
                  modified_service.resetModified();
                  $scope.dropdown_selected_template = _.first($scope.available_templates);
                  Notification.primary('Removed ' + oldTemplate.name);
                });
              };
        }]);