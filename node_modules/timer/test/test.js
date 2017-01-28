(function() {
  var AssertSequence, assert, assertEqual, test4, timer;
  var __slice = Array.prototype.slice;
  if (typeof require !== "undefined" && require !== null) {
    require.paths.unshift(__dirname);
    timer = require('../timer.js').timer;
  } else if (typeof window !== "undefined" && window !== null) {
    timer = window.timer;
  }
  assertEqual = function(msg, x, y) {
    if (x !== y) {
      return console.error(msg, x, y);
    }
  };
  assert = function(b, msg) {
    if (!b) {
      return console.error(msg != null ? msg : 'assertion failed');
    }
  };
  AssertSequence = function(msg) {
    var done;
    done = 0;
    return function() {
      var msg2, msgg, n, ncb;
      msg2 = arguments[0], ncb = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      msgg = msg + ':' + msg2;
      n = 0;
      return function() {
        var a;
        a = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
        if (ncb.length <= n) {
          return console.error(msgg, 'TOO MANY INVOCATIONS own/global:', n + 1, done + 1);
        }
        done++;
        assertEqual(msgg + ': real/expected: ', done, ncb[n++]);
        if (typeof ncb[n] === 'function') {
          return ncb[n++].apply(this, a);
        }
      };
    };
  };
  (function() {
    var seq;
    seq = AssertSequence('#1 timeout functions');
    timer(200, seq('timer 200', 3));
    setTimeout(seq('setTimeout', 2), 190);
    seq('filler', 1)();
    return setTimeout((function() {
      var clear, o;
      seq('setTimeout', 4);
      clear = timer(10, seq('timer 10')).clear;
      clear();
      o = timer(10, seq('timer 10'));
      return timer.clear(o);
    }), 210);
  })();
  (function() {
    var clear, o, seq;
    seq = AssertSequence('#2 interval functions');
    clear = timer(null, 50, seq('50ms timer', 3, 5)).clear;
    seq('begin', 1)();
    timer(75, seq('1', 4));
    timer(110, seq('2', 6));
    timer(110, function() {
      return clear();
    });
    o = timer.interval(10, seq('10ms timer - should trigger once', 2));
    return timer(15, function() {
      return timer.clear(o);
    });
  })();
  (function() {
    var clear, seq;
    seq = AssertSequence('#3 timeout list');
    clear = timer([50, 30], 40, seq('timer', 2, 4, 6, 8)).clear;
    timer(30, seq('30ms', 1));
    timer(60, seq('60ms', 3));
    timer(90, seq('90ms', 5));
    timer(130, seq('130ms', 7));
    timer(170, seq('170ms', 9));
    return timer(165, function() {
      return clear();
    });
  })();
  (test4 = function(i) {
    var clear, j, seq;
    seq = AssertSequence('#4.' + (i || 0) + ' auto adjusting interval');
    j = 1;
    clear = timer.auto(3000, function() {
      var adj;
      seq('adjusted interval', ++j)();
      adj = Date.now() % 3000;
      return assert(adj < 50 || adj > 2950, 'adjusted interval not ok: ' + adj);
    }).clear;
    seq('filler', 1)();
    return timer(6003, function() {
      seq('end', 4)();
      return clear();
    });
  })();
  timer(parseInt(Math.random() * 10000), function() {
    var i, _results;
    _results = [];
    for (i = 1; i <= 500; i++) {
      _results.push(test4(i));
    }
    return _results;
  });
  (function() {
    var clear, j, seq;
    seq = AssertSequence('#4 auto adjusting interval');
    j = 1;
    clear = timer.auto(3000, function() {
      var adj;
      seq('adjusted interval', ++j)();
      adj = Date.now() % 3000;
      return assert(adj < 50 || adj > 2950, 'adjusted interval not ok: ' + adj);
    }).clear;
    seq('filler', 1)();
    return timer(6003, function() {
      seq('end', 4)();
      return clear();
    });
  })();
}).call(this);
