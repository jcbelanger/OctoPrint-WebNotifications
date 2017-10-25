self.addEventListener('push', function(event) {
  var data = event.data.json();
  event.waitUntil(self.registration.showNotification(data.title, data.options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(clients.openWindow('/'));
});