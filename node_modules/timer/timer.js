(function() {
  var clearTimer, timer;
  timer = function(timeouts, interval, cb) {
    var entry, setup, timeouts_i, timeouts_l;
    if (cb === void 0) {
      cb = interval;
      interval = null;
    }
    if (typeof timeouts === 'number') {
      timeouts = [timeouts];
    }
    timeouts_l = (timeouts != null ? timeouts.length : void 0) || 0;
    timeouts_i = 0;
    entry = {
      clear: function() {
        return clearTimer(entry);
      }
    };
    (setup = function(call) {
      if (call) {
        cb();
      }
      if (timeouts_i < timeouts_l) {
        return entry.timeout = setTimeout(setup, timeouts[timeouts_i++], true);
      } else if (interval != null) {
        delete entry.timeout;
        return entry.interval = setInterval(cb, interval);
      }
    })();
    return entry;
  };
  timer.auto = function(interval, cb) {
    return timer(interval - Date.now() % interval, interval, cb);
  };
  timer.interval = function(interval, cb) {
    return timer(null, interval, cb);
  };
  timer.clear = clearTimer = function(entry) {
    if (entry != null ? entry.timeout : void 0) {
      clearTimeout(entry.timeout);
      delete entry.timeout;
    }
    if (entry != null ? entry.interval : void 0) {
      clearInterval(entry.interval);
      return delete entry.interval;
    }
  };
  if (typeof exports !== "undefined" && exports !== null) {
    exports.timer = timer;
  }
  if (typeof define === "function") {
    define([], function() {
      return {
        timer: timer
      };
    });
  }
  if (typeof window !== "undefined" && window !== null) {
    window.timer = timer;
  }
}).call(this);
