self.addEventListener('push', function(event) {
  event.waitUntil(
    self.registration.showNotification('My Title', {
      lang: 'en',
      body: 'Hello World',
      icon: '/static/img/graph-background.png',
      //vibrate: [500, 100, 500],
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});