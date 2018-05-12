import React, { Component } from 'react';
import logo from './logo.svg';
import axios from 'axios';
import { facetree } from './facetree'
import './App.css';
const facetree_backend = 'https://facetree-dev.ardoe.net';

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      //loading: true,
      mode: 'Login'
    }
  }
    login = function (event) {
      console.log('Try to log in')
         axios.post(facetree_backend + "/v1/users/login/password", {
             "email": this.state.username,
             "password": this.state.password
         }).then((response) => {
             this.mode = "Loading";
             console.log('logged in')
             facetree.database_updater(response.data.token, (updated_records) => {
                 this.mode = "Tree";
                 this.curent_individual = facetree.database.root.id;
             });
         }).catch( (error) => {
             console.log(error);
         });
         event.preventDefault();
     }
    parentin = function(id) {
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
     childin = function(id) {
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
     individual = function(id) {
         return facetree.database.individuals[id];
     }
     show_individual = function (id) {
         this.image = '';
         this.curent_individual = id;
         this.mode = 'Individual';
         if (facetree.database.individuals[id].imageIds && facetree.database.individuals[id].imageIds.length > 0) {
             var imgid = facetree.database.individuals[id].imageIds[0][1];
             axios.get(facetree_backend + "/v1/images/" + imgid + "/full.jpg/base64", {"headers": facetree.auth_headers})
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
  return (
    <div id="root">
        { this.state.mode == 'Login' &&
        <form onSubmit={this.login}>
            <label for="uname"><b>Username</b></label>
            <input onChange={event => this.state.username = event.target.value} type="text" placeholder="Enter Username" name="uname" required/>

            <label for="psw"><b>Password</b></label>
            <input onChange={event => this.state.password = event.target.value} type="password" placeholder="Enter Password" name="psw" required/>

            <button type="submit">Login</button>
        </form>
      }

        { this.state.mode == 'Loading' && <div>
            Loading...
        </div>
      }

    </div>
  );
}
}

export default App;
