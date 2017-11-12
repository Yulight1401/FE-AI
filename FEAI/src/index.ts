import {run} from '@cycle/run'
import {makeDOMDriver} from '@cycle/dom'
import {Component} from './interfaces'

import {App} from './app'

import {ActivationFunction, ColorMode, CPPN} from './models/cppn'

document.body.style = 'padding:0px;'
document.body.onload = () => {
    const canvasDom = document.querySelector('#nn_art')
    const cppnInstance = new CPPN(canvasDom)
    cppnInstance.setColorMode('rgb')
    cppnInstance.setActivationFunction('tanh')
    cppnInstance.setNumLayers(2)
    cppnInstance.setZ1Scale(100)
    cppnInstance.setZ2Scale(100)
    cppnInstance.generateWeights(30, .6)
    cppnInstance.start()
}

const main : Component = App

const drivers = {
  DOM: makeDOMDriver('#root')
}

run(main, drivers)
