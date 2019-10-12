import React from 'react'
import * as d3 from "d3";
import { pol2cart, coordAsTransform, colorLookUp } from './utils'

const styles = {
  node: {
    opacity: 1,
  },
  nodeCircle: {
    opacity: 0,
    zIndex: 2,
  },
  nodeText: {
    opacity: 0,
    zIndex: 4,
  },
}
export default function Individual({data: d, onHover, onLeave}) {
  const circleRef = React.createRef()
  const imageId = d.data.imageIds.length ? d.data.imageIds[0][1] : null
  return (
    <g
      className={`individual ${(d.children ? 'node--internal' : 'node--leaf')}`}
      style={styles.node}
      transform={coordAsTransform(pol2cart(d.y, d.x))}
      strokeLinejoin="round"
      strokeWidth={3}
      onMouseEnter={event => {
        if (onHover) {
          const pos = {
            x: event.pageX,
            y: event.pageY,
          }
          onHover(pos, d.data.name, imageId)
        }
        d3.select(circleRef.current).style('stroke', 'black')
        }
      }
      onMouseLeave={event => {
        if (onLeave) onLeave()
        d3.select(circleRef.current).style('stroke', 'none')
        }
      }
    >
      <circle
        r={7}
        style={styles.nodeCircle}
        fill={d.data.color ? colorLookUp[d.data.color] : "#999"}
        ref={circleRef}
      />
      <text
        dy={"0.31em"}
        x={d.x < Math.PI === !d.children ? 8 : -8}
        y={d.children ? (d.x < Math.PI ? 8 : -8) : 0}
        textAnchor={d.x < Math.PI === !d.children ? "start" : "end"}
        transform={"rotate(" + (d.x < Math.PI ? d.x - Math.PI/2.0 : d.x + Math.PI/2.0) * 180 / Math.PI + ")"}
        opacity={0}
        style={styles.nodeText}
      >{d.data.name}</text>
    </g>
  )
}