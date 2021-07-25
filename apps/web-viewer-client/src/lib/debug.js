import _debug from 'debug';

localStorage.debug = '*';

export default function (namespace) {
  const d = _debug(namespace);

  // See https://github.com/visionmedia/debug#output-streams
  d.log = console.log.bind(console);

  return {
    ns: namespace,
    log: d,
    error: _debug(namespace)
  }
}

