/**
 * SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
 * See also https://github.com/seed-platform/seed/main/LICENSE.md
 */
angular.module('BE.seed.service.columns', []).factory('columns_service', [
  '$http',
  'user_service',
  function ($http, user_service) {

    var columns_service = {};

    columns_service.update_column = function (column_id, data) {
      return columns_service.update_column_for_org(user_service.get_organization().id, column_id, data);
    };

    columns_service.create_column_for_org = function (org_id, data) {
      return $http.post('/api/v3/columns/', {
          organization_id: org_id,
          ...data,
      }).then(function (response) {
        return response.data;
      });
    };

    columns_service.update_column_for_org = function (org_id, column_id, data) {
      return $http.put('/api/v3/columns/' + column_id + '/', data, {
        params: {
          organization_id: org_id
        }
      }).then(function (response) {
        return response.data;
      });
    };

    columns_service.rename_column = function (column_id, column_name, overwrite_preference) {
      return columns_service.rename_column_for_org(user_service.get_organization().id, column_id, column_name, overwrite_preference);
    };

    columns_service.rename_column_for_org = function (org_id, column_id, column_name, overwrite_preference) {
      return $http.post('/api/v3/columns/' + column_id + '/rename/', {
        organization_id: org_id,
        new_column_name: column_name,
        overwrite: overwrite_preference
      }).then(function (response) {
        return response;
      }).catch(function (error_response) {
        return {
          data: {
            success: false,
            message: 'Unsuccessful: ' + error_response.data.message
          }
        };
      });
    };

    columns_service.delete_column = function (column_id) {
      return columns_service.delete_column_for_org(user_service.get_organization().id, column_id);
    };

    columns_service.delete_column_for_org = function (org_id, column_id) {
      return $http.delete('/api/v3/columns/' + column_id + '/', {
        params: {organization_id: org_id}
      });
    };

    return columns_service;

  }]);
