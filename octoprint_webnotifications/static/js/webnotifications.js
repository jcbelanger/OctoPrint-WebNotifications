/*
 * View model for OctoPrint-WebNotifications
 *
 * Author: Josh Belanger
 * License: AGPLv3
 */
$(function() {
    function WebnotificationsViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        WebnotificationsViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_webnotifications, #tab_plugin_webnotifications, ...
        [ /* ... */ ]
    ]);
});
