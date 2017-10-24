# coding=utf-8
import json
import octoprint.plugin
from pywebpush import webpush


        
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
    
    def get_template_vars(self):
        return dict(
            public_key=self.get_public_key()
        )
    
    @octoprint.plugin.BlueprintPlugin.route("/push-subscription", methods=["POST"])
    def save_push_subscription(self):
        from flask import request
        from octoprint.server.api import NO_CONTENT
        
        webpush(
            subscription_info=request.get_json(),
            data=json.dumps(dict(
                foo="bar"
            )),
            vapid_private_key=self.get_private_key(),
            vapid_claims=dict(
                sub="mailto:jcbelanger@users.noreply.github.com"
            )
        )
        
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
        
    def get_public_key(self):
        #todo generate keys on install
        return "BBDoBnbKU0ex3GwNprJ0xuOhWCCU5ImO3lexrPpIv2-dUHDn-BtCJMXzf-J32Y1YpPKRyRhVx8tknmLf9bmQn28"

    def get_private_key(self):
        #todo generate keys on install
        return "1Kx0uosM1wWXXEzJnJSNL0UkNJZhIzk_tnZTB0Zdy1E"



def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = WebNotificationsPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		#"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}