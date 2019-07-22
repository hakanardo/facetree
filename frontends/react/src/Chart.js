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
export default class Chart extends Component {

  state = {}

  componentDidMount() {
    this.drawTree()
  }

  componentDidUpdate(prevProps) {
    const { mode } = this.props
    if (prevProps.mode !== mode) {
      const link = d3.selectAll('.link')
        .transition()
        .duration(1500)
        .attr("d", mode === 'Edged' ? makeLinkPath : makeRadialLink)
    }
  }

  drawTree() {
    const root = tree(this.props.data.root)

    const chart = d3.select("#chart")

    const mode = this.props.mode || 'Edged'

    function zoom() {
      treeContainer.attr("transform", d3.event.transform);
    }

    const svg = chart
      .append('svg')
      .style("max-height", "95vh")
      .style("width", "auto")
      .style("font", "10px sans-serif")
      .style("margin", "5px")
      .attr("pointer-events", "all")
      .call(d3.zoom()
          .scaleExtent([1, 8])
          .on("zoom", zoom));

    const treeContainer = svg.append("g")

    const tooltip = chart
      .append("div")
      .style("opacity", 1)
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("top", 0)
      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "5px")
      .style("padding", "5px")

    //console.log(chart.node().getBoundingClientRect())

    function mouseover(d) {
      console.log(d.x, d.y, d.data.alpha, d.data.name)
      tooltip
        .style("opacity", 1)
      d3.select(this).selectAll('circle')
        .style("stroke", "black")
    }

    function mousemove(d) {
      const [mouseX, mouseY] = d3.mouse(this)
      const [x, y] = polToCart(d.x, d.y)
      tooltip
        .html("Personen heter: " + d.data.name)
        .style("left", (d3.event.pageX + 7) + "px")
        .style("top", (d3.event.pageY) + "px")
    }

    function mouseleave(d) {
      tooltip
        .style("opacity", 0)
      d3.select(this).selectAll('circle')
        .style("stroke", "none")
    }

    const yearText = treeContainer.append("text")
      .attr("font-size", "8em")
      .text(startYear)
      .attr("transform", function(d) {
        const width = this.getComputedTextLength()
        return `translate(${-width/2.0}, -25)`
      })

    yearText
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
    const node = treeContainer.append("g").selectAll(".individual")
      .data(root.descendants().reverse())
      .enter().append("g")
      .attr("class", d => "individual" + (d.children ? " node--internal" : " node--leaf"))
      .attr("transform", d => coordAsTransform(pol2cart(d.y, d.x)))
      .attr("stroke-linejoin", "round")
      .attr("stroke-width", 3)
      .style('opacity', 1)
    const link = treeContainer.append("g")
      .selectAll(".link")
      .data(root.links())
      .enter().append("path")
      .attr("class", "link")
      //.style("opacity", 0)
      .attr("fill", "none")
      .attr("stroke", "#555")
      .attr("stroke-width", 1)
      .attr("d", mode === 'Edged' ? makeLinkPath : makeRadialLink)

    const transition = d3.transition('grow').duration(animationSpeed).ease(d3.easeQuadIn)

    link
      .attr("stroke-dasharray", function(d) { return this.getTotalLength() + " " + this.getTotalLength()})
      .attr("stroke-dashoffset", function(d) { return this.getTotalLength()})
      .transition(transition)
      //.delay(d => d.source.data.generation*transition.duration())
      .delay(d => (d.target.data.birth.from - startYear)*transition.duration())
      .style("opacity", 1)
      .attr("stroke", d => d.source.data.color ? colLookUp[d.source.data.color] : "#999")
      //.ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0)

    node
      .transition(transition)
      //.delay(d => (d.data.generation-1)*transition.duration())
      .delay(d => (d.data.birth.from - startYear)*transition.duration())
      .attr("transform", d => coordAsTransform(pol2cart(mode === 'Edged' ? d.data.generation * distanceGen : d.y, d.x)))
      .style('opacity', 1)

    node.append("circle")
      .attr("fill", d => d.data.color ? colLookUp[d.data.color] : "#999")
      .attr("r", 7)
      .attr("opacity", 0)
      .transition(transition)
      //.delay(d => d.data.generation*transition.duration() - transition.duration()/1.5)
      .delay(d => (d.data.birth.from - startYear)*transition.duration())
      .style("opacity", 1)

    node.append("text")
      .attr("dy", "0.31em")
      .attr("x", d => d.x < Math.PI === !d.children ? 9 : -9)
      .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
      .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
      .attr("transform", function(d) { return "rotate(" + (d.x < Math.PI ? d.x - Math.PI/2.0 : d.x + Math.PI/2.0) * 180 / Math.PI + ")"; })
      .attr("opacity", 0)
      .text(d => d.data.name)
      .clone(true).lower()
      //.attr("stroke", "white")
      .transition(transition)
      //.delay(d => d.data.generation*transition.duration())
      .delay(d => (d.data.birth.from - startYear + 1)*transition.duration())
      .attr('opacity', 1)

    node
      .on("mousemove", mousemove)
      .on('mouseover', mouseover)
      .on('mouseout', mouseleave)
      .on('click', toggleChildren)


    const svgNode = svg.node()
    svg.attr("viewBox", autoBox(svgNode))
    this.setState({
      node,
      link,
      svg,
      chart,
      treeContainer
    })
  }

  render() {
    return <div id="chart"></div>
  }


}