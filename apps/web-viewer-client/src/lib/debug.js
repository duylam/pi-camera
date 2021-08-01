import _debug from 'debug';

localStorage.debug = '*';

export default function (namespace) {
  const l = _debug(namespace);
  const e = _debug(namespace)

  // See https://github.com/visionmedia/debug#output-streams
  l.log = console.log.bind(console);
  e.log = console.error.bind(console);

  return {
    ns: namespace,
    log: l,
    error: e
  }
}

