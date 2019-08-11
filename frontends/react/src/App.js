import React, { Component } from 'react';
import logo from './logo.svg';
import axios from 'axios';
import facetree from './facetree'
import './App.css';
import Chart from './Chart'
const facetree_backend = 'https://facetree-dev.ardoe.net';

// test00
// hasYs56
const database = facetree.database

const parseTree = database => {
  const tree = {
    //root: database.root
    root: buildIndividual(database.root)
  }
  return tree
}

const buildIndividual = ind => {
  if (!database.parentin[ind.id]) {
    return ind
  }
  var plist = Array.from(database.parentin[ind.id]);
  let children = []
  for (var parent in plist) {
    const childrenIdsSet = database.families[plist[parent]].children
    var childrenIds = childrenIdsSet ? Array.from(childrenIdsSet) : []
    const parentChildren = childrenIds.map(childId => database.individuals[childId])
    children.push(...parentChildren)
  }
  //ind.children = children
  //children.forEach(buildIndividual)
  return {
    ...ind,
    children: children.map(buildIndividual)
  }
}
class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      //loading: true,
      treeMode: 'Edged',
      animate: false,
      auth: null,
    }
  }
  login = event => {
    console.log('Try to log in')
    axios.post(facetree_backend + "/v1/users/login/password", {
      "email": this.state.username,
      "password": this.state.password
    }).then(response => {
      this.setState({
        auth: response.data.token,
        loading: true,
      })
      console.log('logged in')
      facetree.database_updater(response.data.token, updated_records => {
        console.log(updated_records)
        console.log(facetree.database)
        const treeData = parseTree(facetree.database)
        this.setState({
          treeData,
          loading: false,
        })
      });
    }).catch((error) => {
      console.log(error);
    });
    event.preventDefault();
  }
  parentin = id => {
    var families = [];
    if (!facetree.database.parentin[id]) {
      return [];
    }
    var plist = Array.from(facetree.database.parentin[id]);
    for (var i in plist) {
      let fid = plist[i];
      families.push(facetree.database.families[fid]);
    }
    return families;
  }
  childin = id => {
    var families = [];
    if (!facetree.database.childin[id]) {
      return [];
    }
    var plist = Array.from(facetree.database.childin[id]);
    for (var i in plist) {
      let fid = plist[i];
      families.push(facetree.database.families[fid]);
    }
    return families;
  }
  individual = id => {
    return facetree.database.individuals[id];
  }
  show_individual = id => {
    this.image = '';
    this.curent_individual = id;
    this.mode = 'Individual';
    if (facetree.database.individuals[id].imageIds && facetree.database.individuals[id].imageIds.length > 0) {
      var imgid = facetree.database.individuals[id].imageIds[0][1];
      axios.get(facetree_backend + "/v1/images/" + imgid + "/full.jpg/base64", { "headers": facetree.auth_headers })
        .then((response) => {
          this.image = 'data:image/jpeg;base64,' + response.data;
        })
        .catch(function (error) {
          console.log("Image download failed");
          console.log(error);
        });
    }
  }
  render() {
    const { treeData, treeMode, animate, loading, auth } = this.state
    return (
      <div id="root">
        {!auth && (
        <form onSubmit={this.login}>
          <label for="uname"><b>Username</b></label>
          <input onChange={event => this.state.username = event.target.value} type="text" placeholder="Enter Username" name="uname" required />

          <label for="psw"><b>Password</b></label>
          <input onChange={event => this.state.password = event.target.value} type="password" placeholder="Enter Password" name="psw" required />

          <button type="submit">Login</button>
        </form>
        )}
        {loading && <h3>Laddar...</h3>}
        {auth && treeData && (
          <div>
            <button onClick={() => this.setState({treeMode: 'Edged'})}>Edged</button>
            <button onClick={() => this.setState({treeMode: 'Smooth'})}>Smooth</button>
            <button onClick={() => this.setState(state => ({animate: !state.animate}))}>Animate</button>
            <Chart data={treeData} mode={treeMode} animate={animate} />
          </div>
        )}
      </div>
    );
  }
}

export default App;
