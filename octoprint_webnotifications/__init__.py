# coding=utf-8

import octoprint.plugin

        
class WebNotificationsPlugin(octoprint.plugin.StartupPlugin,
               octoprint.plugin.TemplatePlugin,
               octoprint.plugin.SettingsPlugin,
               octoprint.plugin.AssetPlugin,
               octoprint.plugin.BlueprintPlugin):
    
    def on_after_startup(self):
        self._logger.info("Hello World! (more: %s)" % self._settings.get(["url"]))

    def get_settings_defaults(self):
        return dict(url="https://en.wikipedia.org/wiki/Hello_world")

    def get_assets(self):
        return dict(
            js=["js/webnotifications.js"],
        )
    
    @octoprint.plugin.BlueprintPlugin.route("/push-subscription", methods=["POST"])
    def save_push_subscription(self):
        from flask import request
        from octoprint.server.api import NO_CONTENT

        subscription = request.get_json()

        self._logger.info("NEW SUB!!!!!!!!!!!!!!!!!!!!!!!!! %s" % subscription['endpoint'])
        return NO_CONTENT

    def is_blueprint_protected(self):
        return False

    def get_update_information(self):
		return dict(
			webnotifications=dict(
				displayName="Web Notifications Plugin",
				displayVersion=self._plugin_version,
				type="github_release",
				user="jcbelanger",
				repo="OctoPrint-WebNotifications",
				current=self._plugin_version,
				pip="https://github.com/jcbelanger/OctoPrint-WebNotifications/archive/{target_version}.zip"
			)
		)


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = WebNotificationsPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}