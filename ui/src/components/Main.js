import React from 'react';
import { Switch, Route } from 'react-router-dom';
import PrivateRoute from './PrivateRoute';
import LayoutPanel from './panel';
import LayoutContainer from './layout/container';
import LayoutForm from './form/LayoutForm';
import UploadForm from './form/UploadForm';
import LoginContainer from './login';
import Error404 from './util/error/Error404';
import Error500 from './util/error/Error500';


const Main = () => (
  <main>
    <Switch>
      <PrivateRoute exact path="/" component={LayoutPanel} />
      <Route path="/login" component={LoginContainer} />
      <PrivateRoute path="/layouts/new" component={LayoutForm} />
      <PrivateRoute path="/layouts/:id/init" component={UploadForm} />
      <PrivateRoute path="/layouts/:id" component={LayoutContainer} />
      <Route path="/error/500" component={Error500} />
      <Route component={Error404} />
    </Switch>
  </main>
);

export default Main;
