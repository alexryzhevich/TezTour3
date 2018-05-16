import React from 'react';
import Header from './components/header';
import Main from './components/Main';
import Loading from './components/loading';
import Errorhandler from './components/ErrorHandler';
import './App.css';

const App = () => (
  <div className="App">
    <Header />
    <Main />
    <Loading />
    <Errorhandler />
  </div>
);

export default App;
