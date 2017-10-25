# coding=utf-8
import time, os, json, sqlite3, octoprint.plugin
from octoprint.events import Events
from contextlib import closing, contextmanager
from py_vapid import Vapid, b64urlencode
from pywebpush import webpush, WebPushException

        
class WebNotificationsPlugin(octoprint.plugin.StartupPlugin,
                octoprint.plugin.SettingsPlugin,
                octoprint.plugin.AssetPlugin,
                octoprint.plugin.TemplatePlugin,
                octoprint.plugin.BlueprintPlugin,
                octoprint.plugin.EventHandlerPlugin):

    def on_startup(self, host, port):
        with self.get_db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT NOT NULL PRIMARY KEY,
                    subscription TEXT NOT NULL
                )
            ''')
            db.commit()

    def get_settings_defaults(self):
		return dict(
			vapid_key_file=os.path.join(self.get_plugin_data_folder(), "private_key.pem"),
            database_file=os.path.join(self.get_plugin_data_folder(), "subscriptions.db"),
			print_done=dict(
				title="Print job finished!",
				body="{file} finished printing in {elapsed_time}"
			)
		)

    def get_assets(self):
        return dict(
            js=["js/webnotifications.js"],
        )

    def get_template_vars(self):
        return dict(
            application_server_key=self.get_application_server_key()
        )

    def on_event(self, event, payload):
        if event == Events.PRINT_DONE:
            self._logger.info("Sending print done event notification")

            placeholders = dict(
                file=os.path.basename(payload["file"]),
                elapsed_time=elapsed_time(payload["time"]),
            )

            self.notify_all(
                notification_title=self._settings.get(["print_done", "title"]).format(**placeholders),
                notification_options=dict(
                    body=self._settings.get(["print_done", "body"]).format(**placeholders)
                ),
            )

    def is_blueprint_protected(self):
        return False

    @octoprint.plugin.BlueprintPlugin.route("/push-subscription", methods=["POST"])
    def save_push_subscription(self):
        from flask import request        
        from octoprint.server.api import NO_CONTENT

        subscription = request.get_json()
        id = subscription["endpoint"]
        self.save_push_subscription_db(id, subscription)
        
        return NO_CONTENT
    
    def get_vapid(self):
        return Vapid.from_file(self._settings.get(["vapid_key_file"]))

    def get_application_server_key(self):
        return b64urlencode(self.get_vapid().public_key.public_numbers().encode_point())

    @contextmanager
    def get_db(self):
        with closing(sqlite3.connect(self._settings.get(["database_file"]))) as db:
            db.row_factory = sqlite3.Row
            yield db

    @contextmanager
    def get_push_subscriptions_db(self):
        with self.get_db() as db:
            with closing(db.cursor()) as cur:
                rows = cur.execute("SELECT subscription FROM subscriptions")
                yield (json.loads(row["subscription"]) for row in rows)

    def get_push_subscription_db(self, id):
        with self.get_db() as db:
            with closing(db.cursor()) as cur:
                cur.execute("SELECT subscription FROM subscriptions WHERE id = ?", (id,))
                subscription = cur.fetchone()["subscriptions"]
                return json.loads(subscription)

    def save_push_subscription_db(self, id, subscription):
        with self.get_db() as db:
            db.execute(
                "INSERT OR REPLACE INTO subscriptions (id, subscription) VALUES (?, ?)", 
                (id, json.dumps(subscription))
            )
            db.commit()
            self._logger.info("New subscription!")

    def delete_push_subscription_db(self, id):
        with self.get_db() as db:
            db.execute("DELETE FROM subscriptions VALUES id = ?)", (id,))
            db.commit()
            db.info("Deleted subscription!")

    def get_web_push_args(self, notification_title=None, notification_options=None, vapid_claims=None):
        if notification_title is None:
            notification_title = "OctoPrint"
        
        notification_options_defaults = dict(
            icon="/static/img/graph-background.png",
            timestamp=time.time(),
        )
        if notification_options is None:
            notification_options = notification_options_defaults
        else:
            notification_options_defaults.update(notification_options)
            notification_options = notification_options_defaults
        
        vapid_claims_defaults = dict(
            sub="mailto:jcbelanger@users.noreply.github.com"
        )
        if vapid_claims is None:
            vapid_claims = vapid_claims_defaults
        else:
            vapid_claims_defaults.update(vapid_claims)
            vapid_claims = vapid_claims_defaults
        
        return dict(
            vapid_private_key=self._settings.get(["vapid_key_file"]),
            vapid_claims=vapid_claims,
            data=json.dumps(dict(
                title=notification_title,
                options=notification_options
            )),
        )

    def notify_one(self, id, notification_title=None, notification_options=None, vapid_claims=None):
        web_push_args = self.get_web_push_args(notification_title, notification_options, vapid_claims)
        sub = self.get_push_subscription_db(id)
        try:
            webpush(subscription_info=sub, **web_push_args)
            return True
        except WebPushException as err:
            self._logger.error(err)
            return False

    def notify_all(self, notification_title=None, notification_options=None, vapid_claims=None):
        web_push_args = self.get_web_push_args(notification_title, notification_options, vapid_claims)
        all_success = True
        with self.get_push_subscriptions_db() as subs:
            for sub in subs:
                try:
                    webpush(subscription_info=sub, **web_push_args)
                except WebPushException as err:
                    self._logger.error(err)
                    all_success = False
        return all_success

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


def elapsed_time(seconds, granularity=2):
    intervals = [
        ('week', 60 * 60 * 24 * 7),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1),
    ]
    
    result = []
    for name, duration in intervals:
        count, seconds = divmod(seconds, duration)
        if count > 0:
            if count != 1:
                name = name + 's'
            result.append("%s %s" % (int(count), name))
    return ', '.join(result[:granularity]) or 'instantly'


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = WebNotificationsPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}