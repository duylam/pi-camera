const _debug = require('debug');

_debug.enable('*');

module.exports = function (namespace) {
  const d = _debug(namespace);

  // See https://github.com/visionmedia/debug#output-streams
  d.log = console.log.bind(console);

  return {
    ns: namespace,
    log: d,
    error: _debug(namespace)
  }
}

