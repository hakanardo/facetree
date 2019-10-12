import React from 'react'
import * as d3 from "d3";
import { pol2cart, colorLookUp } from './utils'


const distanceGen = 140;

export function makeLinkPath(d) {
  const ind = d.source.data
  const child = d.target.data
  const gen = ind.generation
  const indAlpha = d.source.x
  const childAlpha = d.target.x
  const distRing = (gen+1) * distanceGen - distanceGen/2.0
  const indPos = gen === 1 ? {x: 0, y: 0} : pol2cart(gen * distanceGen, indAlpha)
  const indRingPos = pol2cart(distRing, indAlpha)
  const childRingPos = pol2cart(distRing, childAlpha)
  const childPos = pol2cart((gen+1) * distanceGen, childAlpha)
  const line1 = ['M', indPos.x, indPos.y, 'L', indRingPos.x, indRingPos.y]
  const line2 = ['M', childRingPos.x, childRingPos.y, 'L', childPos.x, childPos.y]
  let startAngle = childAlpha;
  let endAngle = indAlpha;
  if (indAlpha < childAlpha) {
      startAngle = indAlpha;
      endAngle = childAlpha;
  }
  let largeArc = 0;
  let sweep = 1;
  if (endAngle - startAngle > Math.PI) {
      largeArc = 1;
      if (endAngle - startAngle > 3 * Math.PI/4) {
          largeArc = 0
          sweep = 0
      }
  }
  const arcPos1 = pol2cart(distRing, startAngle)
  const arcPos2 = pol2cart(distRing, endAngle)
  const arc = ['M', arcPos1.x, arcPos1.y, 'A', distRing, distRing, 0, largeArc, sweep, arcPos2.x, arcPos2.y]
  const path = [...line2, ...line1, ...arc]
  return path.join(' ')
}

export const makeRadialLink = d3.linkRadial().angle(d => d.x).radius(d => d.data.generation*distanceGen)

const styles = {
    fill: "none",
    opacity: 0,
    //stroke: "#555",
    strokeWidth: 1,
    zIndex: 1,
}

export function Link({data, mode}) {
  return (
    <path
      className="link"
      style={styles}
      stroke={data.source.data.color ? colorLookUp[data.source.data.color] : "#999"}
      d={mode === 'Edged' ? makeLinkPath(data) : makeRadialLink(data)}
    />
  )
}
export default Link