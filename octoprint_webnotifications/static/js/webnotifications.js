(function() {
  
  function askNotificationPermission() {
    return new Promise(function(resolve, reject) {
      //handle callback/promise API variations
      var permissionResult = Notification.requestPermission(resolve);
      if (permissionResult) {
        permissionResult.then(resolve, reject);
      }
    })
    .then(function(permissionResult) {
      if (permissionResult !== 'granted') {
        throw new Error(permissionResult);
      }
    });
  }
  
  function subscribeToPush() {
    return navigator.serviceWorker.register(WebNotifications.SERVICE_WORKER_JS)
      .then(function(registration) {
        return registration; //TODO find workaround for chrome's navigator.serviceWorker.ready
      })
      .then(function(registration) {
          var subscriptionOptions = {
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(WebNotifications.APPLICATION_SERVER_KEY)
          }
          return registration.pushManager.subscribe(subscriptionOptions)
            .catch(function() {
              return registration.pushManager.getSubscription()
                .then(function(subscription) {
                  return subscription && subscription.unsubscribe()
                })
                .then(function() {
                  return registration.pushManager.subscribe(subscriptionOptions);
                });
            });
      });
  }
  
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
  
  function savePushSubscription(subscription) {
    return fetch(WebNotifications.SAVE_PUSH_SUBSCRIPTION, {
        method: 'POST',
        headers: {
          'Content-type': 'application/json'
        },
        cache: 'no-store',
        body: JSON.stringify(subscription.toJSON()),
      })
      .then(function(response) {
        if (!response.ok) {
          throw new Error(response.statusText);
        }
        return response;
      });
  }
  
  function isBrowserSupported() {
    return 'serviceWorker' in navigator && 'PushManager' in window;
  }
  
  if(isBrowserSupported()) {
    askNotificationPermission()
      .then(subscribeToPush)
      .then(savePushSubscription)
      .then(function() {
        console.warn("celebrate");
      })
      .catch(function(err) {
        console.error('ServiceWorker registration failed: ', err);
      });
  }
})();
