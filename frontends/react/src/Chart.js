import React, { Component } from 'react'
import * as d3 from "d3";

const distanceGen = 140;
const genCount = 7
const width = (2 * genCount + 10) * distanceGen;
const height = width
const animationSpeed = 150
const startYear = 1810
const endYear = 2019
const colLookUp = {'blå': 'blue', 'grön': 'green', 'gul': 'yellow', 'röd': 'red'};

function autoBox(node) {
  const { x, y, width, height } = node.getBBox();
  return [x, y, width, height];
}
const tree = data => d3.tree()
  .size([2 * Math.PI, 800]) // polar coordinate system
  //.size([width, height])
  .separation((a, b) => {
    return (a.parent == b.parent ? 1 : 2) / a.depth
  })
  (d3.hierarchy(data))

const polToCart = (theta, r) => [r * Math.cos(theta), r * Math.sin(theta)]
const pol2cart = (r, theta) => ({
  x: r * Math.cos(theta - Math.PI/2),
  y: r * Math.sin(theta - Math.PI/2)
})

const coordAsTransform = cart => `translate(${cart.x}, ${cart.y})`
const toggleChildren = d => {
  if (d.children) {
      d._children = d.children;
      d.children = null;
  } else if (d._children) {
      d.children = d._children;
      d._children = null;
  }
  return d;
}

function makeLinkPath(d) {
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
const makeRadialLink = d3.linkRadial().angle(d => d.x).radius(d => d.data.generation*distanceGen)

const styles = {
  tooltip: {
    opacity: 0,
    position: "absolute",
    top: 0,
    backgroundColor: "white",
    border: "solid",
    borderWidth: 2,
    borderRadius: 5,
    padding: 5,
  },
  svg: {
    maxHeight: "95vh",
    width: "100%",
    font: "10px sans-serif",
    margin: 5,
  },
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
  link: {
    fill: "none",
    opacity: 0,
    //stroke: "#555",
    strokeWidth: 1,
    zIndex: 1,
  },
}

function Individual({data: d, onHover, onLeave}) {
  const circleRef = React.createRef()
  return (
    <g
      className={`individual ${(d.children ? 'node--internal' : 'node--leaf')}`}
      style={styles.node}
      transform={coordAsTransform(pol2cart(d.y, d.x))}
      strokeLinejoin="round"
      strokeWidth={3}
      onMouseEnter={event => {
        if (onHover) {
          onHover({
            x: event.pageX,
            y: event.pageY,
          }, d.data.name)
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
        fill={d.data.color ? colLookUp[d.data.color] : "#999"}
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

function Link({data, mode}) {
  return (
    <path
      className="link"
      style={styles.link}
      stroke={data.source.data.color ? colLookUp[data.source.data.color] : "#999"}
      d={mode === 'Edged' ? makeLinkPath(data) : makeRadialLink(data)}
    />
  )
}
export default class Chart extends Component {

  chartRef = React.createRef()
  nodesRef = React.createRef()
  linksRef = React.createRef()
  svgRef = React.createRef()
  treeRef = React.createRef()
  yearTextRef = React.createRef()
  
  state = {
    tooltipDynamicStyle: {},
    tooltipText: '',
  }

  componentDidMount() {
    this.updateD3(this.props)
  }

  componentDidUpdate(prevProps) {
    const { mode, animate } = this.props
    if (prevProps.mode !== mode) {
      const link = d3.selectAll('.link')
        .transition()
        .duration(1500)
        .attr("d", d => mode === 'Edged' ? makeLinkPath(d) : makeRadialLink(d))
    }
    if (prevProps.data !== this.props.data) {
      console.log('data changed')
      this.updateD3(prevProps)
    }
    if (prevProps.animate !== animate) {
      if (animate) {
        this.queueTransitions()
      } else {
        const svg = d3.select(this.svgRef.current)
        svg.selectAll('.individual').interrupt('grow').selectAll('*').interrupt('grow')
        svg.selectAll('.link').interrupt('grow')
        d3.select(this.yearTextRef.current).interrupt()
      }
    }
  }

  queueTransitions() {
    console.log('queing transitions')
    const root = tree(this.props.data.root)

    const treeNodes = root ? root.descendants().reverse() : []

    d3.select(this.yearTextRef.current)
      .transition()
      .duration(animationSpeed)
      .on("start", function repeat() {
        d3.active(this)
            .tween("text", function() {
              const that = d3.select(this)
              const nextYear = parseInt(that.text())+1
              if (nextYear > endYear) that.interrupt()
              //const interpolate = d3.interpolateNumber(that.text().replace(/,/g, ""), parseInt(that.text())+1)
              return function(t) { that.text(nextYear); };
            })
          .transition()
          .on("start", repeat);
      });

    const nodes = d3.select(this.nodesRef.current)

    const transition = d3.transition('grow').duration(animationSpeed).ease(d3.easeQuadIn)

    const links = d3.select(this.linksRef.current)

    links.selectAll('.link')
      .data(root.links())
      //.attr('stroke-dasharray', function(d) { this.getTotalLength() + " " + d.node.getTotalLength()})
      //.attr('stroke-dashoffset', function(d) { this.getTotalLength()})
      .transition(transition)
      .delay(d => (d.target.data.birth.from - startYear)*transition.duration())
      .style("opacity", 1)
      //.ease(d3.easeLinear)
      //.attr("stroke-dashoffset", 0)

    const nodesData = nodes.selectAll('.individual').data(treeNodes)

    nodesData
      .transition(transition)
      .delay(d => (d.data.birth.from - startYear) * transition.duration())
      .attr("transform", d => coordAsTransform(pol2cart(this.props.mode === 'Edged' ? d.data.generation * distanceGen : d.y, d.x)))
      .style('opacity', 1)

    nodes.selectAll('circle')
      .data(treeNodes)
      .transition(transition)
      .delay(d => (d.data.birth.from - startYear)*transition.duration())
      .style("opacity", 1)

    nodes.selectAll('text')
      .data(treeNodes)
      .transition(transition)
      .delay(d => (d.data.birth.from - startYear + 1)*transition.duration())
      .style('opacity', 1)
  }

  updateD3() {

    const svg = d3.select(this.svgRef.current)
    const treeContainer = d3.select(this.treeRef.current)

    const zoom =
      d3.zoom()
      .scaleExtent([1, 8])
      .on("zoom", () => treeContainer.attr("transform", d3.event.transform))
    svg
      .call(zoom)
      .call(zoom.transform, d3.zoomIdentity.translate(100, 50).scale(1.5))

    const yearText = d3.select(this.yearTextRef.current)
    yearText
      .attr("transform", function(d) {
        const width = this.getComputedTextLength()
        return `translate(${-width/2.0}, -25)`
      })

  }

  closeTooltip = () => {
    this.setState({
      tooltipDynamicStyle: {
        opacity: 0,
      },
      tooltipText: ""
    })
  }

  openTooltip = (pos, text, imageId) => {
    this.setState({
      tooltipDynamicStyle: {
        opacity: 1,
        left: pos.x,
        top: pos.y + 7,
      },
      tooltipText: text,
      tooltipImg: null,
    })
    if (imageId) {
      facetree.get_image(imageId).then(imageData => {
        this.setState({tooltipImg: 'data:image/jpeg;base64,' + imageData})
      })
      .catch(error => {
          console.log("Image download failed")
          console.log(error)
      });
    }
  }

  render() {
    //const { treeRoot, links } = this.state
    const { data, mode } = this.props
    const { tooltipDynamicStyle, tooltipText, tooltipImg } = this.state
    const treeRoot = tree(data.root)
    const treeNodes = treeRoot ? treeRoot.descendants().reverse() : []
    const links = treeRoot ? treeRoot.links() : []
    return (
      <div ref={this.chartRef}>
        <div id="tooltip" style={{
          ...styles.tooltip,
          ...tooltipDynamicStyle,
        }}>
          <p>{tooltipText}</p>
          {tooltipImg && <img src={tooltipImg}/>}
        </div>
        <svg
          style={styles.svg}
          pointerEvents="all"
          ref={this.svgRef}
          viewBox={[-height/2, -width/2, height, width]}
          // width={width}
          // height={height}
        >
          <g ref={this.treeRef}>
            <text style={{fontSize: '8em'}} ref={this.yearTextRef}>{startYear}</text>
            <g ref={this.linksRef}>
              {links.map((link, i) => <Link key={i} mode={mode} data={link} />)}
            </g>
            <g ref={this.nodesRef}>
              {treeNodes.map(node => <Individual data={node} onHover={this.openTooltip} onLeave={this.closeTooltip} onClick={this.openModal} />)}
            </g>
          </g>
        </svg>
      </div>
    )
  }


}