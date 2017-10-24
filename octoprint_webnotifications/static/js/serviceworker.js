self.addEventListener('push', function(event) {
  var data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'OctoPrint', 
      Object.assign(data, {
        lang: 'en',
        icon: '/static/img/graph-background.png',
        timestamp: Math.floor(Date.now())
      })
    )
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});