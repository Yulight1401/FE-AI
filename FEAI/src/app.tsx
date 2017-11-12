import xs from 'xstream'
import {Sources, Sinks} from './interfaces'

export function App(sources : Sources) : Sinks {

  const vtree$ = xs.of(
    <canvas id = 'nn_art' style ='position:absolute; left: 0; top: 0;width: 100%; height: 100%;'></canvas>
  )

  return {
    DOM: vtree$
  }
}
