/*
 * View model for OctoPrint-WebNotifications
 *
 * Author: Josh Belanger
 * License: AGPLv3
 */ 
$(function() {
  
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
        return registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(WebNotifications.VAPID_PUBLIC_KEY)
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
      body: JSON.stringify(subscription),
    })
    .then(function(response) {
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      return response;
    });
  }
  
  function isBrowserCapable() {
    return 'serviceWorker' in navigator && 'PushManager' in window;
  }
  
  if (isBrowserCapable()) {
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
});
