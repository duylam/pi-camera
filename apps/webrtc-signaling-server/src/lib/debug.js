const _debug = require('debug');

_debug.enable('*');

module.exports = function (namespace) {
  const d = _debug(`${namespace} [debug]`);
  const e = _debug(`${namespace} [error]`);

  return {
    log: d,
    error: e
  }
}

