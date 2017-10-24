# coding=utf-8
import time, os, json, sqlite3, octoprint.plugin
from contextlib import closing, contextmanager
from py_vapid import Vapid, b64urlencode
from pywebpush import webpush, WebPushException

        
class WebNotificationsPlugin(octoprint.plugin.StartupPlugin,
                octoprint.plugin.ShutdownPlugin,
                octoprint.plugin.TemplatePlugin,
                octoprint.plugin.SettingsPlugin,
                octoprint.plugin.AssetPlugin,
                octoprint.plugin.BlueprintPlugin):
    
    def on_startup(self, host, port):
        self._vapid = Vapid.from_file(self.get_vapid_key_file())
        self._db = sqlite3.connect(self.get_database_file())
        self._db.executescript(
            '''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT NOT NULL PRIMARY KEY,
                subscription TEXT NOT NULL
            );
            '''
        )
        self._db.commit()
    
    def on_shutdown(self):
        self._db.close()
        self._db = None
    
    def get_vapid_key_file(self):
        return os.path.join(self.get_plugin_data_folder(), "private_key.pem")
    
    def get_database_file(self):
        return os.path.join(self.get_plugin_data_folder(), "subscriptions.db")

    def get_assets(self):
        return dict(
            js=["js/webnotifications.js"],
        )
    
    def get_template_vars(self):
        return dict(
            application_server_key=b64urlencode(self._vapid.public_key.public_numbers().encode_point())
        )
    
    @octoprint.plugin.BlueprintPlugin.route("/push-subscription", methods=["POST"])
    def save_push_subscription(self):
        from flask import request        
        from octoprint.server.api import NO_CONTENT

        subscription = request.get_json()
        id = subscription["endpoint"]
        self.save_push_subscription_db(id, subscription)
        self.notify_one(id, title="Test Notification", body="It works!")
        
        return NO_CONTENT
    
    def save_push_subscription_db(self, id, subscription):
        self._db.execute(
            "INSERT OR REPLACE INTO subscriptions (id, subscription) VALUES (?, ?)", 
            (id, json.dumps(subscription))
        )
        self._db.commit()
        self._logger.info("New subscription!")
    
    def delete_push_subscription_db(self, id):
        self._db.execute("DELETE FROM subscriptions VALUES id = ?)", (id,))
        self._db.commit()
        self._logger.info("Deleted subscription!")      

    @contextmanager
    def get_push_subscriptions_db(self):
        with closing(self._db.cursor()) as cur:
            rows = cur.execute("SELECT subscription FROM subscriptions")
            yield (json.loads(row[0]) for row in rows)
    
    def get_push_subscription_db(self, id):
        with closing(self._db.cursor()) as cur:
            cur.execute("SELECT subscription FROM subscriptions WHERE id = ?", (id,))
            result = cur.fetchone()
            subscription = result[0]
            return json.loads(subscription)
    
    def get_web_push_args(self, *args, **kwargs):
        notification = dict(
            title="OctoPrint",
            lang="en",
            icon="/static/img/graph-background.png",
            timestamp=time.time(),
        )
        notification.update(kwargs)
        return dict(
            data=json.dumps(notification),
            vapid_private_key=self.get_vapid_key_file(),
            vapid_claims=dict(
                sub="mailto:jcbelanger@users.noreply.github.com"
            )
        )
        
    def notify_one(self, id, *args, **kwargs):
        web_push_args = self.get_web_push_args(*args, **kwargs)
        sub = self.get_push_subscription_db(id)
        try:
            webpush(subscription_info=sub, **web_push_args)
            return True
        except WebPushException as err:
            self._logger.error(err)
            return False
        
    
    def notify_all(self, *args, **kwargs):
        web_push_args = self.get_web_push_args(*args, **kwargs)
        all_success = True
        with self.get_push_subscriptions_db() as subs:
            for sub in subs:
                try:
                    webpush(subscription_info=sub, **web_push_args)
                except WebPushException as err:
                    self._logger.error(err)
                    all_success = False
        return all_success

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
		#"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}