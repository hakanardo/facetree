const colorLookUp = {'blå': 'blue', 'grön': 'green', 'gul': 'yellow', 'röd': 'red'};

const pol2cart = (r, theta) => ({
  x: r * Math.cos(theta - Math.PI/2),
  y: r * Math.sin(theta - Math.PI/2)
})

const coordAsTransform = cart => `translate(${cart.x}, ${cart.y})`

export {
    colorLookUp,
    pol2cart,
    coordAsTransform,
}